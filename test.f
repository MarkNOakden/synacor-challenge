      program test
      implicit none
      integer :: A = 4, B = 1, H, FN
      write(*,*) 'A=', A
      write(*,*) 'B=', B
      write(*,*) 'H=', H
      do H = 0, 32767
         write(*, *) 'H, FN', H, FN(A, B, H)
      end do ! H
      end program

      recursive integer function fn(A, B, H) result (FN_RES)
      integer :: A, B, H

      if ( A .eq. 0 ) then
         FN_RES = MOD(B + 1, 32768)
         return
      end if
      
      if ( B .eq. 0 ) then
         FN_RES = fn(A - 1, H, H)
         return
      end if

      FN_RES = fn(A - 1, fn(A, B - 1, H), H)
      return
      end function
