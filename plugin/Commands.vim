" make
map <F4> :let &makeprg="cd ../build/Release/CLang && ninja"
map <F5> :make<CR>
map <F6> :call <SID>ToggleQf()<cr>

function! s:ToggleQf()
  for buffer in tabpagebuflist()
    if bufname(buffer) == ''
      " then it should be the quickfix window
      cclose
      return
    endif
  endfor

  copen
endfunction
