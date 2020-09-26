" make
map <F5> :Build<CR>
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

