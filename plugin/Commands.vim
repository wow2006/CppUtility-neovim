" make
map <F4> :let &makeprg="cd ../build/Release/CLang && ninja"
map <F5> :make<CR>
map <F6> :call <SID>ToggleQf()<cr>

function! s:CloseQF()
  for buffer in tabpagebuflist()
    if bufname(buffer) == ''
      " then it should be the quickfix window
      cclose
      return 1
    endif
  endfor
  return 0
endfunction

function! s:ToggleQf()
  if s:CloseQF()
    return
  endif

  copen
endfunction

let s:compile_commands=execute(":pwd") . "/compile_commands.json"
call writefile([s:compile_commands], "/home/ahussein/test")
if filereadable(s:compile_commands)
  echo "SpecificFile exists"
endif

