# zsh-glint internals; sourced inside the entry point's local option scope.
# SPDX-License-Identifier: MIT
typeset -g TC_ENABLED=${TC_ENABLED:-1}
typeset -g TC_STYLE=${TC_STYLE:-fg=8}
typeset -g TC_MIN_PREFIX=${TC_MIN_PREFIX:-2}
typeset -g TC_MAX_BUFFER=${TC_MAX_BUFFER:-512}
typeset -g TC_HISTORY_LIMIT=${TC_HISTORY_LIMIT:-1000}
typeset -g TC_INIT_COMPLETION=${TC_INIT_COMPLETION:-1}
typeset -ga _tc_history=()
typeset -g _tc_suffix='' _tc_source_buffer=''
typeset -g _tc_version=0.2.0
typeset -g _tc_cache_input='' _tc_cache_value=''
typeset -gi _tc_cache_valid=0 _tc_cache_min=0 _tc_cache_max=0

_tc_refresh_history() {
  emulate -L zsh
  local key entry
  local -i limit=1000
  [[ $TC_HISTORY_LIMIT == <1-100000> ]] && limit=$TC_HISTORY_LIMIT
  _tc_history=()
  _tc_cache_valid=0
  # Sort only at prompt boundaries, never on each keystroke.
  local -a keys=( ${(Onk)history} )
  for key in "${(@)keys[1,$limit]}"; do
    entry=${history[$key]}
    [[ -n $entry && $entry != [[:space:]]* && $entry != *[[:cntrl:]]* ]] || continue
    _tc_history+=( "$entry" )
  done
  return 0
}

# Pure prefix matcher: input is always data, never evaluated as shell code.
_tc_suggest() {
  emulate -L zsh
  local prefix=$1 entry
  local -i minimum=2 maximum=512
  [[ $TC_MIN_PREFIX == <1-1024> ]] && minimum=$TC_MIN_PREFIX
  [[ $TC_MAX_BUFFER == <1-65536> ]] && maximum=$TC_MAX_BUFFER
  REPLY=''
  [[ $TC_ENABLED == 1 && ${#prefix} -ge $minimum && ${#prefix} -le $maximum ]] || return 0
  [[ $prefix != [[:space:]]* && $prefix != *[[:cntrl:]]* ]] || return 0
  if (( _tc_cache_valid && minimum == _tc_cache_min && maximum == _tc_cache_max )) && [[ $prefix == "$_tc_cache_input" ]]; then
    REPLY=$_tc_cache_value
    return 0
  fi
  # Use Zsh's native array search; quote pattern characters supplied by the user.
  local pattern="${(b)prefix}?*"
  entry=${_tc_history[(r)${~pattern}]}
  if (( ${#entry} > maximum )); then
    # A too-long first match must not hide a later candidate within the limit.
    local candidate
    entry=''
    for candidate in "${(@M)_tc_history:#${~pattern}}"; do
      if (( ${#candidate} <= maximum )); then entry=$candidate; break; fi
    done
  fi
  [[ -z $entry ]] || REPLY=${entry[${#prefix}+1,-1]}
  _tc_cache_input=$prefix
  _tc_cache_value=$REPLY
  _tc_cache_min=$minimum
  _tc_cache_max=$maximum
  _tc_cache_valid=1
  return 0
}

_tc_clear() {
  emulate -L zsh
  if [[ -n $_tc_suffix && $POSTDISPLAY == "$_tc_suffix" ]]; then
    POSTDISPLAY=''
  fi
  region_highlight=( "${(@)region_highlight:#*memo=zsh-glint}" )
  _tc_suffix=''
  _tc_source_buffer=''
  return 0
}

_tc_redraw() {
  emulate -L zsh
  _tc_clear
  [[ $TC_ENABLED == 1 && $KEYMAP != vicmd && $CONTEXT == start ]] || return 0
  (( CURSOR == ${#BUFFER} && ! PENDING && ! KEYS_QUEUED_COUNT && ! REGION_ACTIVE )) || return 0
  # Do not take ownership of text displayed by another plugin.
  [[ -z $POSTDISPLAY ]] || return 0
  local REPLY
  _tc_suggest "$BUFFER"
  [[ -n $REPLY ]] || return 0
  _tc_source_buffer=$BUFFER
  _tc_suffix=$REPLY
  POSTDISPLAY=$REPLY
  region_highlight+=( "${#BUFFER} $(( ${#BUFFER} + ${#REPLY} )) $TC_STYLE memo=zsh-glint" )
  return 0
}

_tc_accept() {
  emulate -L zsh
  if [[ $TC_ENABLED == 1 && -n $_tc_suffix && $BUFFER == "$_tc_source_buffer" && $POSTDISPLAY == "$_tc_suffix" ]] && (( CURSOR == ${#BUFFER} )); then
    BUFFER+=$_tc_suffix
    CURSOR=${#BUFFER}
    _tc_clear
    return 0
  fi
  return 1
}

_tc_forward_char() {
  _tc_accept || zle _tc_saved_forward_char -- "$@"
}
_tc_vi_forward_char() {
  _tc_accept || zle _tc_saved_vi_forward_char -- "$@"
}
_tc_accept_widget() {
  _tc_accept || return 0
}
_tc_toggle_widget() {
  emulate -L zsh
  if [[ $TC_ENABLED == 1 ]]; then TC_ENABLED=0; else TC_ENABLED=1; fi
  _tc_clear
  zle -R
}

_tc_doctor() {
  emulate -L zsh
  local -i warnings=0
  local name hook expected audit
  local -a hook_widgets
  print -r -- "zsh-glint $_tc_version — doctor"
  print -r -- "PASS Zsh $ZSH_VERSION (requires 5.9+)"
  if (( ${+_TC_LOADED} )); then
    print -- 'PASS Plugin loaded'
  else
    print -- 'WARN Plugin unloaded; open a new Zsh session or source the plugin again'
    (( ++warnings ))
  fi
  for name in TC_ENABLED TC_INIT_COMPLETION; do
    if [[ ${(P)name} == (0|1) ]]; then
      print -r -- "PASS $name"
    else
      print -r -- "WARN $name must be 0 or 1"
      (( ++warnings ))
    fi
  done
  for name in TC_MIN_PREFIX TC_MAX_BUFFER TC_HISTORY_LIMIT; do
    case $name in
      TC_MIN_PREFIX) expected='<1-1024>' ;;
      TC_MAX_BUFFER) expected='<1-65536>' ;;
      TC_HISTORY_LIMIT) expected='<1-100000>' ;;
    esac
    if [[ ${(P)name} == ${~expected} ]]; then
      print -r -- "PASS $name"
    else
      print -r -- "WARN $name is out of range; runtime uses its default"
      (( ++warnings ))
    fi
  done
  if (( ${+_comps} )); then
    print -- 'PASS Native completion initialized'
  else
    print -- 'WARN Native completion missing; run: autoload -Uz compinit; compinit'
    (( ++warnings ))
  fi
  autoload -Uz compaudit
  if audit=$(compaudit 2>/dev/null); then
    print -- 'PASS Completion directory permissions'
  else
    print -- 'WARN Completion directory audit failed; run compaudit to inspect paths'
    (( ++warnings ))
  fi
  for name in forward-char vi-forward-char; do
    expected="user:_tc_${name//-/_}"
    if [[ ${widgets[$name]} == "$expected" ]]; then
      print -r -- "PASS $name wrapper"
    else
      print -r -- "WARN $name was replaced; inspect plugin order or bind zsh-glint-accept explicitly"
      (( ++warnings ))
    fi
  done
  for hook expected in line-pre-redraw _tc_redraw line-finish _tc_clear; do
    hook_widgets=()
    zstyle -a "zle-$hook" widgets hook_widgets
    if [[ ${widgets[zle-$hook]} == "user:azhw:zle-$hook" && -n ${hook_widgets[(r)*:$expected]} ]]; then
      print -r -- "PASS $hook hook"
    else
      print -r -- "WARN $hook hook missing or replaced; load zsh-glint after other hook providers"
      (( ++warnings ))
    fi
  done
  if [[ -n ${precmd_functions[(r)_tc_refresh_history]} ]]; then
    print -- 'PASS History refresh hook'
  else
    print -- 'WARN History refresh hook missing; source the plugin in a fresh session'
    (( ++warnings ))
  fi
  if (( ${+functions[_zsh_autosuggest_start]} )); then
    print -- 'WARN Another history-suggestion provider is loaded; enable only one provider'
    (( ++warnings ))
  fi
  print -r -- "INFO Cached history entries: ${#_tc_history} (command contents omitted)"
  [[ $TC_ENABLED != 0 ]] || print -- 'INFO Suggestions are intentionally disabled; use zsh-glint on to enable'
  print -r -- "Result: $warnings warning(s). No files or configuration changed."
  (( warnings == 0 ))
}

zsh-glint() {
  emulate -L zsh
  case ${1:-status} in
    on) TC_ENABLED=1 ;;
    off) TC_ENABLED=0 ;;
    toggle) if [[ $TC_ENABLED == 1 ]]; then TC_ENABLED=0; else TC_ENABLED=1; fi ;;
    status) print -r -- "zsh-glint $_tc_version | enabled=$TC_ENABLED | history=${#_tc_history} | zsh=$ZSH_VERSION" ;;
    doctor) _tc_doctor ;;
    refresh) _tc_refresh_history ;;
    unload)
      # A later wrapper can retain our function by alias. Rewrapping that chain
      # would make it call itself through the overwritten saved widget.
      if [[ ${widgets[forward-char]} != user:_tc_forward_char || ${widgets[vi-forward-char]} != user:_tc_vi_forward_char ]]; then
        typeset -g _TC_RELOAD_BLOCKED=1
      fi
      add-zsh-hook -d precmd _tc_refresh_history
      add-zle-hook-widget -d line-pre-redraw _tc_redraw
      add-zle-hook-widget -d line-finish _tc_clear
      # Restore only widgets we still own; preserve later plugin changes.
      if [[ ${widgets[forward-char]} == user:_tc_forward_char ]]; then
        zle -A _tc_saved_forward_char forward-char
      fi
      if [[ ${widgets[vi-forward-char]} == user:_tc_vi_forward_char ]]; then
        zle -A _tc_saved_vi_forward_char vi-forward-char
      fi
      TC_ENABLED=0
      unset _TC_LOADED
      _tc_history=()
      _tc_cache_valid=0
      print -- 'zsh-glint unloaded; native completion remains available.'
      ;;
    help|--help|-h)
      print -- 'Usage: zsh-glint [on|off|toggle|status|doctor|refresh|unload]'
      ;;
    *) print -u2 -- "Unknown command: $1"; return 2 ;;
  esac
}

# Preserve the public command used by existing installations.
terminal-completion() { zsh-glint "$@"; }

autoload -Uz add-zsh-hook add-zle-hook-widget
zmodload zsh/parameter
if [[ $TC_INIT_COMPLETION == 1 ]] && (( ! ${+_comps} )); then
  autoload -Uz compinit
  # Standard security checks are retained. No global completion styles changed.
  compinit || return 1
fi
zle -A forward-char _tc_saved_forward_char
zle -A vi-forward-char _tc_saved_vi_forward_char
zle -N forward-char _tc_forward_char
zle -N vi-forward-char _tc_vi_forward_char
zle -N zsh-glint-accept _tc_accept_widget
zle -N zsh-glint-toggle _tc_toggle_widget
zle -N terminal-completion-accept _tc_accept_widget
zle -N terminal-completion-toggle _tc_toggle_widget
zle -N _tc_redraw
zle -N _tc_clear
add-zsh-hook precmd _tc_refresh_history
add-zle-hook-widget line-pre-redraw _tc_redraw
add-zle-hook-widget line-finish _tc_clear
_tc_refresh_history
typeset -g _TC_LOADED=1
