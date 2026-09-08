# zsh-glint — native Zsh history suggestions and completion.
# SPDX-License-Identifier: MIT
[[ -o interactive ]] || return 0
autoload -Uz is-at-least
if ! is-at-least 5.9; then
  print -u2 -- 'zsh-glint requires Zsh 5.9 or newer.'
  return 1
fi
(( ${+_TC_LOADED} )) && return 0

# Keep the caller's shell options intact, including aliases during loading.
() {
  emulate -L zsh
  setopt localoptions no_aliases
  typeset -g TC_ENABLED=${TC_ENABLED:-1}
  typeset -g TC_STYLE=${TC_STYLE:-fg=8}
  typeset -g TC_MIN_PREFIX=${TC_MIN_PREFIX:-2}
  typeset -g TC_MAX_BUFFER=${TC_MAX_BUFFER:-512}
  typeset -g TC_HISTORY_LIMIT=${TC_HISTORY_LIMIT:-1000}
  typeset -g TC_INIT_COMPLETION=${TC_INIT_COMPLETION:-1}
  typeset -ga _tc_history=()
  typeset -g _tc_suffix='' _tc_source_buffer=''

  _tc_refresh_history() {
    emulate -L zsh
    local key entry
    local -i limit=1000
    [[ $TC_HISTORY_LIMIT == <1-100000> ]] && limit=$TC_HISTORY_LIMIT
    _tc_history=()
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
    for entry in "${_tc_history[@]}"; do
      if [[ $entry == "$prefix"* && $entry != "$prefix" && ${#entry} -le $maximum ]]; then
        REPLY=${entry[${#prefix}+1,-1]}
        return 0
      fi
    done
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

  zsh-glint() {
    emulate -L zsh
    case ${1:-status} in
      on) TC_ENABLED=1 ;;
      off) TC_ENABLED=0 ;;
      toggle) if [[ $TC_ENABLED == 1 ]]; then TC_ENABLED=0; else TC_ENABLED=1; fi ;;
      status) print -r -- "zsh-glint 0.1.0 | enabled=$TC_ENABLED | history=${#_tc_history} | zsh=$ZSH_VERSION" ;;
      refresh) _tc_refresh_history ;;
      unload)
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
        print -- 'zsh-glint unloaded; native completion remains available.'
        ;;
      help|--help|-h)
        print -- 'Usage: zsh-glint [on|off|toggle|status|refresh|unload]'
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
}
