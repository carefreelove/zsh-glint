# Shared managed-block editor. Invoked by install.zsh / uninstall.zsh.
emulate -L zsh
setopt err_exit no_unset pipe_fail
typeset action=$1
shift
typeset rc_path=${ZDOTDIR:-$HOME}/.zshrc
while (( $# )); do
  case $1 in
    --rc)
      (( $# >= 2 )) || { print -u2 -- '--rc requires a path'; exit 2; }
      rc_path=$2; shift 2 ;;
    --help|-h)
      print -- "Usage: zsh scripts/${action}.zsh [--rc /path/to/.zshrc]"
      exit 0 ;;
    *) print -u2 -- "Unknown argument: $1"; exit 2 ;;
  esac
done
typeset project_dir=${${(%):-%x}:A:h:h}
typeset begin='# >>> zsh-glint >>>'
typeset end='# <<< zsh-glint <<<'
typeset legacy_begin='# >>> terminal-completion >>>'
typeset legacy_end='# <<< terminal-completion <<<'
typeset expected_end=''
typeset line tmp_file='' backup=''
typeset -a kept=()
integer inside=0 blocks=0
rc_path=${rc_path:A}
[[ ! -d $rc_path ]] || { print -u2 -- "Not a file: $rc_path"; exit 1; }
if [[ -e $rc_path ]]; then
  while IFS= read -r line || [[ -n $line ]]; do
    if [[ $line == "$begin" || $line == "$legacy_begin" ]]; then
      (( inside == 0 && blocks == 0 )) || { print -u2 -- 'Invalid or duplicate managed block; file unchanged.'; exit 1; }
      inside=1; blocks=1
      if [[ $line == "$begin" ]]; then expected_end=$end; else expected_end=$legacy_end; fi
    elif [[ $line == "$end" || $line == "$legacy_end" ]]; then
      [[ $inside == 1 && $line == "$expected_end" ]] || { print -u2 -- 'Invalid managed block; file unchanged.'; exit 1; }
      inside=0
    elif (( ! inside )); then
      kept+=( "$line" )
    fi
  done < "$rc_path"
fi
(( inside == 0 )) || { print -u2 -- 'Unclosed managed block; file unchanged.'; exit 1; }
if [[ $action == uninstall && $blocks == 0 ]]; then
  print -- "No managed installation found in $rc_path"
  exit 0
fi
if [[ $action == install ]]; then
  [[ -r $project_dir/zsh-glint.plugin.zsh ]] || exit 1
  kept+=( "$begin" "source ${(q)project_dir}/zsh-glint.plugin.zsh" "$end" )
fi
command mkdir -p -- "${rc_path:h}"
tmp_file=$(command mktemp "${rc_path}.tmp.XXXXXXXX")
trap '[[ -z $tmp_file ]] || command rm -f -- "$tmp_file"' EXIT
if [[ -e $rc_path ]]; then
  command cp -p -- "$rc_path" "$tmp_file"
fi
{ for line in "${kept[@]}"; do print -r -- "$line"; done } > "$tmp_file"
if [[ -e $rc_path ]] && command cmp -s -- "$rc_path" "$tmp_file"; then
  print -- "Already up to date: $rc_path"
  exit 0
fi
if [[ -e $rc_path ]]; then
  backup=$(command mktemp "${rc_path}.backup.XXXXXXXX")
  command cp -p -- "$rc_path" "$backup"
fi
command mv -f -- "$tmp_file" "$rc_path"
tmp_file=''
print -- "$action complete: $rc_path"
[[ -z $backup ]] || print -- "Backup: $backup"
if [[ $action == install ]]; then
  print -- 'Open a new Zsh session to activate. Keep this project directory in place.'
else
  print -- 'Open a new Zsh session, or run: zsh-glint unload'
fi
