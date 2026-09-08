# zsh-glint — a little light on your command line.
# SPDX-License-Identifier: MIT
[[ -o interactive ]] || return 0
(( ${+_TC_LOADED} )) && return 0

() {
  builtin 'emulate' -L zsh
  builtin 'setopt' no_aliases
  if [[ ${_TC_RELOAD_BLOCKED:-0} == 1 ]]; then
    builtin 'print' -u2 -- 'zsh-glint: another plugin retained a wrapped widget; open a new Zsh session before reloading.'
    return 1
  fi
  builtin 'autoload' -Uz is-at-least
  if ! is-at-least 5.9; then
    builtin 'print' -u2 -- 'zsh-glint requires Zsh 5.9 or newer.'
    return 1
  fi
  builtin 'source' "${${(%):-%x}:A:h}/lib/glint.zsh"
}
