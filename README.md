# CppUtility-neovim
neovim plugin which have some cpp uility 

install
-------

```bash
if [  -n "$(uname -a | grep Ubuntu)" ]; then
  sudo apt install clang-tidy
else
  sudo pacman -S clang
fi  
```

add to plugin

```vimrc
function! DoRemote(arg)
  UpdateRemotePlugins
endfunction

Plug 'wow2006/CppUtility-neovim', { 'do': function('DoRemote') }
```
