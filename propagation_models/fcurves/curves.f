*
************************************************************************
*
      program curves
*
************************************************************************
*  This program will compute the field strength at a given distance    *
*  or the distance for a given field strength or the erp for a         *
*  given field strength at a given distance using the FM and TV        *
*  propagation curves.  These propagation curves are nonlinear and     *
*  there is no simple formula one can use.                             *
*                                                                      *
*  ERP/HAAT combinations for FM are considered equivalent when the     *
*  separate ERP/HAAT generate a 60 dBu contour at the same distance.   *
*  This definiton was established in the 1940s for FM, TV.             *
*                                                                      *
*                                                                      *
*  Note: Gary Kalagian, original author for much of the following      *
*  code, retired from the FCC in 1999.                                 *
*                                                                      *
*  Options for use of the F(50,90) curves for Digital Television have  *
*  been added (2003).                                                  *
*                                                                      *
*  This program is made available at the user's own risk.  There is no *
*  guarantee made or implied that the program will compile on any      *
*  given system and no statement is made concerning the accuracy of    *
*  this program as compared to any other source, official or           *
*  unofficial.  Code has not been optimized nor is it supported.       *
*                                                                      *
*  This code was compiled as a console program using Compaq Visual     *
*  Fortran, version 6.  It will also compile as a console program      *
*  using the Fortran complier used with lcc-win32. Changes may be      *
*  needed -- particularly in curves.f -- to run this on other systems. *
*  In particular, PC file names such as c:\temp\--- must contain the   *
*  single \ in CVF, c:\temp\filename, while other compilers such as    *
*  lcc-win32 require double \\,  c:\\temp\\filename.  Search for "c:"  *
*  to locate these instances.                                          *
*                                                                      *
*  The folder c:\temp must exist before this program can write output  *
*  to the file c:\temp\FMTVcurves.txt.  This file is overwritten each  *
*  time the program is run.                                            *
*                                                                      *
*  This curves.f implementation is a modification of the original      *
*  curves.f program used on the FCC's VAX machine in the 1980s.        *
************************************************************************
*
      implicit none

      character*1  in

! Listed data values are now assigned after the definition of variables,
! instead of being immediately defined, to satisfy more compilers.

      character*8  input
      character*8  erp_in          ! / '1       ' /
      character*20 hat_in          !  / '1000    ' /
      character*1  dist_unit       !/ 'K' /
      character*8  freq_in         !/ '98.7    ' /
      character*2  flag            !/ '  ' /
      character*2  mikm            !/ '  ' /
      character*2  ahaat           !/ '  ' /
      character*48 flag_message
      character*8  dist_in         !/ '100' /
      character*8  field_in        !/ '60' /
      character*19 aservice(6)     !/ 'Channels 2-6 & FM  ',
 !    &                           'TV Channels  7-13  ',
 !    &                           'TV Channels 14-69  ',
 !    &                           'Digital TV Ch 2-6  ',
 !    &                           'Digita1 TV Ch 7-13 ',
 !    &                           'Digital TV Ch 14-69' /

      character*3  aerp(2)         !/ 'kW ', 'dBk' /

      character*3  curvs(3)        !/ '50', '10', '90' /

      character*4  inx(2)          !/ 'dbu', 'mv/m' /

      integer power_unit           !/ 1 /
      integer fs_unit              !/ 1 /
      integer fs_or_dist           !/ 2 /
      integer prop_curve           !/ 0 /
      integer DTVcurve             !/ 0 /
      integer service              !/ 1 /
      integer fs_dist_erp          !/ 2 /
      integer error_flag
      integer ichan
      integer length, curve_max

      integer save                 !/ 0 /

! Function types
      character*8 f2a
      integer a2i
      real    a2f


      real field
      real distance
      real  field_for_erp
      real power_in
      real power_out
      real erp
      real erpx
      real haat
      real haatx

      erp      = 1.0
      haatx    = 1000.0
      field    = 60.0
      field_for_erp = 60.0
      distance = 100.0

      dist_in = '100'
      field_in = '60'

!Initial selection values

      power_unit = 1
      fs_unit    = 1
      fs_dist_erp  = 2
      prop_curve = 0
      DTVcurve   = 0
      service    = 1
      save       = 0

	  curve_max = 0

      aerp(1) = 'kW '
      aerp(2) = 'dBk'

      curvs(1) = '50'
      curvs(2) = '10'
      curvs(3) = '90'

      inx(1) = 'dBu'
      inx(2) = 'mV/m'

      aservice(1) = 'Channels 2-6 & FM   '
      aservice(2) = 'TV Channels  7-13   '
      aservice(3) = 'TV Channels 14-69   '
      aservice(4) = 'Digital TV Ch 2-6   '
      aservice(5) = 'Digita1 TV Ch 7-13  '
      aservice(6) = 'Digital TV Ch 14-69 '

      erp_in = '1       '
      hat_in = '1000    '
      dist_unit = 'K'
      freq_in   = '98.7    '
      flag      = '  '
      mikm      = '  '
      ahaat     = '  '

*
************************************************************************
*     Print the Welcome message and some instructions.                 *
************************************************************************
*


1     write ( 6, 100 )
100   format (///'            Welcome to CURVES' //
     &        'CURVES lets you compute the distance to a contour;' /
     &        ' the field strength at a given distance; or the ERP'/
     &        ' to produce a given contour at a given distance using'/
     &        ' the FM or NTSC TV F(50,50) or F(50,10) propagation'
     &        ' curves.'//
     &        ' F(50,90) curves have been added for digital television.'
     &          //
     &        'In addition to answering the questions asked,' /
     &        ' "STOP", "NEW", and "BACK" are valid responses.' ///
     &        'Default answers are in [ ]. To use a default answer,'/
     &        ' press the RETURN key.'/// )

      write (6,101)
 101  format("Press ENTER to continue ..."//)


      read(*, 104, err=175, end=900) in

      if(in.eq.'') then
         go to 175
      else
         call stop_new_back( in(1:1), *900, *1, *1)
       end if

 175  continue

************************************************************************
* Find out if the user wants to save a copy of the results to a local  *
* file.                                                                *
************************************************************************

      write(6,102)
      write(6,202)
      write(6,203)
 102  format("  Do you want to save the results to a text file?  [Y]")
 202  format("    (This will overwrite any earlier session.)")
 203  format("*** Selection ['Y' or Enter ] --> " $)

      read(5, '(A)', err=175, end=900) in

      if(in(1:1).eq.' '.or.in(1:1).eq.'Y'.or.in(1:1).eq.'y' .or.
     &   in(1:1).eq.'1')	 then

 205     open(7, file='c:\\temp\\FMTVcurves.txt',
     &     status='unknown', form='formatted', err=402,
     &     access='sequential' )

	   write(6, 302)
 302  format(/"***  Output from this session will be saved at"/
     &       "     c:\\temp\\FMTVcurves.txt ***" ///)
	   save = 1
         go to 2   ! File successfully opened
      else
	     go to 602 ! File cannot be opened
      end if

 402  write(6,403)

 403  format("*** A file could not be opened.  Please check to see if "/
     &"the directory c:\\temp\\ exists.  You may need to create it. "
     &"***" //)

 602  close(7, status = "delete")
      save = 0


*
************************************************************************
*     Get the distance units from the user.                            *
************************************************************************
*
 2     call clear_string(input)

      write ( 6, 103 ) dist_unit(1:(length(dist_unit)))
103   format (/' Distances:' /
     &         '     M or 2 = feet & miles' /
     &         '     K or 1 = meters & km ' /
     &         '*** Selection [ 'A' ] --> ' $  )

      read ( 5, 104, end=900, err=2 ) input
104   format ( a )

      call upper ( input )

	if ( input(1:1) .eq. ' ' )  input='K'

      call stop_new_back ( input(1:1), *900, *1, *175 )

      dist_unit = input(1:1)

4     if ( dist_unit .eq. 'M' .or. dist_unit.eq. '2' ) then
         mikm  = 'mi'
         ahaat = 'ft'
	   dist_unit = 'M'
      else if ( dist_unit .eq. 'K' .or. dist_unit.eq. '1' ) then
         mikm  = 'km'
         ahaat = 'm '
	   dist_unit = 'M'
      else
	   !Default value
         dist_unit = 'K'
         go to 2
      endif
*
************************************************************************
*     Get the power units from the user.                               *
************************************************************************
*
6     call clear_string(input)

      write ( 6, 106 ) power_unit
106   format (/' Power units:' /
     &         '     1 = kW'  /
     &         '     2 = dBk' /
     &         '*** Selection [', i1, '] --> ' $ )

      read ( 5, 104, end=900, err=6 ) input

	if ( input(1:1) .eq. ' ' ) then
	   input = '1'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *2 )
      end if

	power_unit = a2i(input)

	if ( power_unit .eq. 1 .or. power_unit .eq. 2 ) then
	   go to 8
      else      ! Default value
         power_unit = 1
         go to 6
      end if
*
************************************************************************
*     Get the field strength units from the user.                      *
************************************************************************
*
8     call clear_string(input)

      write ( 6, 108 ) fs_unit
108   format (/' Field Strength units:' /
     &         '     1 = dBu' /
     &         '     2 = mV/m' /
     &         '*** Selection [', i1, '] --> ' $)

      read ( 5, 104, end=900, err=6 ) input

	if ( input(1:1) .eq. ' ' ) then
	   input = '1'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *6 )
      end if

	fs_unit = a2i(input)

      if ( fs_unit .eq. 1 .or. fs_unit .eq. 2 ) then
	   if(fs_unit.eq.1) inx(fs_unit) = 'dBu'
	   if(fs_unit.eq.2) inx(fs_unit) = 'mV/m'
	   if(fs_unit.eq.2) field_in = '1.0' ! mV/m = 60 dBu
	   go to 10
      else     !Default value
         fs_unit = 1
         go to 8
      end if
************************************************************************
*     Get the channel range from the user.                             *
************************************************************************
*
10    call clear_string(input)

      write ( 6, 110 ) service
110   format (/' Service:' /
     &         '     1 = TV channels   2 - 6  (analog) or FM' /
     &         '     2 = TV channels   7 - 13 (analog)' /
     &         '     3 = TV channels  14 - 69 (analog)' //
     &         '     4 = DTV channels  2 - 6  (digital)' /
     &         '     5 = DTV channels  7 - 13 (digital)' /
     &         '     6 = DTV channels 14 - 69 (digital)' //

     &         '*** Selection [', i1, '] --> ' $)

      read ( 5, 104, end=900, err=10 ) input

	if ( input(1:1) .eq. ' ' ) then
	   input = '1'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *8 )
      end if

	service = a2i(input)

      if ( service.eq.1.or.service.eq.2.or.service.eq.3 ) then
	   curve_max = 1
	   go to 12
      else if ( service.eq.4.or.service.eq.5.or.service.eq.6 ) then
	   curve_max = 2
	   go to 12
      else
         !Default value
         service = 1
         go to 10
      end if
*
************************************************************************
*     Set a dummy channel number for each service.                     *
*     This dummy channel is used in tvfmfs_metric.f to select the      *
*     proper propagations curves data tables.  Picking different       *
*     channels in the same range (say channels 7 to 13) does not       *
*     change the results.                                              *
************************************************************************

12    if ( service .eq. 1 .or. service.eq.4 ) then
         ichan = 3
!  TV Channels 2 to 6 VHF (North America) & FM (88-108 MHz)

      else if ( service .eq. 2 .or. service .eq. 5 ) then
!  TV Channels 7 to 13 VHF (North America)
         ichan = 9

      else if ( service .eq. 3. or. service .eq. 6 ) then
         ichan = 20
!  TV Channels 14 to 83 UHF (North America)
      end if
      
      
*
************************************************************************
*     Get the time percentage of the propagation curve from the user.  *
*                                                                      *
*     50,50 = received field strength exceeds the selected field       *
*              strength 50% of the locations on a given contour,       *
*              50% of the time  (FM & NTSC service contours)           *
*                                                                      *
*     50,10 = received field strength exceeds the selected field       *
*              strength 50% of the locations on a given contour,       *
*              10% of the time  (Interfering contours)                 *
*                                                                      *
*     50,90 = received field strength exceeds the selected field       *
*              strength 50% of the locations on a given contour,       *
*              90% of the time  (Digital Television service)           *                                        *
*                                                                      *
************************************************************************
*
14    call clear_string(input)

      if( service.eq.1 .or. service.eq.2 .or. service.eq.3) then
        write ( 6, 114 ) prop_curve
114     format (/' Propagation Curve:' /
     &         '     0 = F(50,50) -- Service contours' /
     &         '     1 = F(50,10) -- Interfering Contours' /
     &         '*** Selection [', i1.1, '] --> ' $ )

      else if( service.eq.4 .or. service.eq.5 .or. service.eq.6) then
        write ( 6, 214 ) prop_curve
214     format (/' Propagation Curve:' /
     &         '     1 = F(50,10) -- Interfering Contours' /
     &         '     2 = F(50,90) -- DTV Service Contours' /
     &         '*** Selection [', i1.1, '] --> ' $ )
      end if



      read ( 5, 104, end=900, err=6 ) input

      if ( input(1:1) .eq. ' ' ) then
	   input = '0'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *10 )
      end if

      prop_curve = a2i(input)


      if(( service.eq.4 .or. service.eq.5 .or. service.eq.6) .and.
     &   (prop_curve.le. 0)) then
	        prop_curve = -1
			go to 14
	 ! F(50,50) curves not used for DTV

      else if(( service.eq.1 .or. service.eq.2 .or. service.eq.3) .and.
     &   (prop_curve.ge.2)) then
	        prop_curve = 0
	        go to 14
	 ! F(50,90) curves not used for FM or NTSC (analog) TV
	  end if


      if ( prop_curve .ge. 0 .or. prop_curve .le. 2 ) then
	   go to 16
      else if ( prop_curve .gt. curve_max .or. prop_curve .lt. 0) then
	   go to 16
      else
         ! Default value
         prop_curve = 1
         go to 14
      end if
*
************************************************************************
*     Get the type of output from the user.                            *
************************************************************************
*
16    call clear_string(input)

      if (service.eq.1) then
	  ! Option 3 is available for FM only
      ! Not set up to work with other TV services
      ! Uses 60 dBu (1 mV/m) contour for comparison

          write ( 6, 116 )
 116      format (/' Desired output:' /
     &         '     1 = Field Strength, given Distance;' /
     &         '     2 = Distance, given Field Strength;')



	    if(service.eq.1 .and. prop_curve.eq. 0) write (6,117)
 117      format('     3 = ERP, given Distance and Field Strength.')

	      write(6,118) fs_dist_erp
 118      format('*** Selection [', i1, '] --> ' $ )

      else if (service.eq.2 .or. service.eq.3) then
          write ( 6, 216 ) fs_dist_erp
216       format (/' Desired output:' /
     &         '     1 = Field Strength, given Distance;' /
     &         '     2 = Distance, given Field Strength;' /
     &         '*** Selection [', i1, '] --> ' $ )


      else if (service.ge. 4) then
	  ! Option 3 is NOT available for DTV
          write ( 6, 316 ) fs_dist_erp
316       format (/' Desired output:' /
     &         '     1 = Field Strength, given Distance;' /
     &         '     2 = Distance, given Field Strength;' /
     &         '*** Selection [', i1, '] --> ' $ )
      end if


      read ( 5, 104, end=900, err=6 ) input

	if ( input(1:1) .eq. ' ' ) then
         ! Default value
	   input = '2'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *14 )
      end if

	fs_dist_erp = a2i(input)

      if( fs_dist_erp.eq.1 .or. fs_dist_erp.eq.2 .or. fs_dist_erp.eq.3 )
     &   then
	   go to 17
      else
         fs_dist_erp = 2
         go to 16
      end if

17    call clear_string(input)


*
************************************************************************
*     Get the ERP from the user, except for option 3: assume erp = 1 kw*
************************************************************************
*

      if ( fs_dist_erp .eq. 3 ) then
c
         erp = 1.0
         erp_in='1.0'
         fs_unit = 1
         power_unit = 1

      else
c

         write ( 6, 128 ) aerp( power_unit ), erp_in(1:(length(erp_in)))
 128     format ( / '*** Enter ERP (' A ') [ ' A ' ] --> ' $ )

         read ( 5, 104, end=900, err=6 ) input


	   if ( input .eq. '  ') then
	     input = erp_in
         else
	     call upper(input)
	     call stop_new_back ( input(1:1), *900, *1, *16 )
         end if

	   erp    = a2f(input)
!	   erp_in = f2a(erp)
	   erpx   = erp

	   call stop_new_back ( input(1:1), *900, *1, *16 )

	   if ( power_unit .eq. 2 .and. fs_dist_erp .ne. 3 )
     & 	erpx = 10. ** ( erp / 10. )

         if( erpx .lt. 0.001) then
	     write(6,131)
131      format(/"*** For an input ERP of less than 0.001 kW, "/"    the
     & ERP is reset to 0.001 kW (1 watt). ***"/)
	     erpx   = 0.001
	     erp    = 0.001
	     erp_in = '0.001'
	     go to 20


         else if (erpx .gt. 5100. ) then
           write ( 6, 122 )
122      format (/' *** The ERP must be less than 5100 kW.'/'    Please
     &reenter the ERP.***'/)
             go to 17

         else
             go to 20
         end if

	end if



*
************************************************************************
*     Get the antenna height above average terrain (HAAT) from the user.                                      *
************************************************************************
*
20    continue

      write(6,124) ahaat(1:(length(ahaat))), hat_in(1:(length(hat_in)))
124   format ( / '*** Enter HAAT ('A') [ ' A ' ] --> ' $)

      read ( 5, 104, end=900, err=20 ) input

	if ( input .eq. ' ' ) then
	   input = hat_in
      else
	   call upper(input)

          if(fs_dist_erp .eq.3) then
            call stop_new_back ( input, *900, *1, *16 )
          else
	        call stop_new_back ( input, *900, *1, *17 )
	      end if

          haat  = a2f(input)
	      haatx = haat
          hat_in = f2a(haat)

      end if

	if(haat < 30.) then
	    write (6,177)
	    if(save.eq.1) write(7,177)
177       format(/"*** For a HAAT less than 30 meters,"/
     &"    calculations are made assuming a HAAT of 30 meters. ***"/)
          haatx = 30.

	else if (haat > 1600.) then
	    write (6,178)
	    if(save.eq.1) write(7,178)
178   format(/"*** For a HAAT greater than 1600 meters,"/
     &"    calculations are made assuming a HAAT of 1600 meters. ***"/)
          haatx = 1600.

      end if
      
************************************************************************
*     If the user wants field strength, get the distance.              *
************************************************************************
*
40    continue   ! recycle for next calculation
c
      if ( fs_dist_erp .eq. 1 ) then
*
         write ( 6, 127 ) mikm, dist_in(1:(length(dist_in)))
127      format ( /'*** Distance (' A ') [ ' A ' ] --> ' $)

      read ( 5, 104, end=900, err=6 ) input

	if ( input .eq. ' ' ) then
	   input = dist_in
      else if(input(1:1).eq.'-') then  ! No negative values
	   input(1:1) = '+'
      else
	   call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *20)
      end if


	distance  = a2f(input)
	if(distance .lt.0.0) distance = distance * (-1)

	dist_in = f2a(distance)

************************************************************************
*     if the user wants distance, get the field strength.              *
************************************************************************
*
      else if ( fs_dist_erp .eq. 2 ) then
*
121      continue


         write ( 6, 130 ) inx(fs_unit), field_in(1:(length(field_in)))
130      format ( /, '*** Field  (' A ') [ ' A ' ] --> ' $)

      read ( 5, 104, end=900, err=6 ) input

	if ( input .eq. ' ' ) then
	   input = field_in
      else if(input(1:1).eq.'-') then  ! No negative values
	   input(1:1) = '+'
      end if

         call upper(input)
         call stop_new_back ( input(1:1), *900, *1, *20 )

         field = a2f(input)
	   field_in = f2a(field)

*
************************************************************************
*     If the user wants ERP, get distance and field strength.          *
************************************************************************
*
      else if ( fs_dist_erp .eq. 3 ) then
c
45     continue

       write(6,126) mikm(1:(length(mikm))), dist_in(1:(length(dist_in)))
126    format ( /, '*** Distance (' A ') [ ' A ' ] --> ' $)

       read ( 5, 104, end=900, err=40 ) input

       call upper ( input )
	   if ( input .eq. ' ' ) then
	      input = dist_in
         else if(input(1:1).eq.'-') then  ! No negative values
	   input(1:1) = '+'
	   end if

         call stop_new_back ( input(1:1), *900, *1, *20 )
         distance = a2f(input)

*
         if ( distance .le. 0.0 ) then

               dist_in = '100'
               distance = 100.0
               go to 45
         end if


	     field = 60.
! Results may not be consistent at other field strengths
! Calculations are done at 60 dBu = 1 mV/m, initial power is 1.0 kW
	     field_in = f2a(field)

         erp=1.0
         erpx=1.0


c



      end if
*
************************************************************************
*     Change user inputs to the arguments needed for tvfmfs_metric.    *
************************************************************************
*
 50   continue
*
      if ( mikm .eq. 'mi' ) distance = distance * 1.609344
*
      if ( fs_unit .eq. 2 ) then
c
         field = 20.0 * log10 ( field * 1000.0 )
         field_for_erp = 20.0 * log10 ( field_for_erp * 1000.0 )
c
      end if
c
      if      ( fs_dist_erp .eq. 1 ) then
         fs_or_dist = 1
      else if ( fs_dist_erp .eq. 2 ) then
         fs_or_dist = 2
      else if ( fs_dist_erp .eq. 3 ) then
         fs_or_dist = 1
	end if

************************************************************************
! TEST- Show Input Results or Default Values
!
!       write(6,500) erpx
! 500  format("ERP =" F10.5 "  ")
!      write(6,501) haatx
! 501  format("HAAT =" F10.5 "  ")
!       write(6,502) field
! 502  format("Field =" F10.5 "  ")
!       write(6,503) distance
! 503  format("Distance =" F10.5 "  ")
!       write(6,504) prop_curve, service, fs_dist_erp  
! 504  format("prop_curve=",I1,"  service=",I1,"  fs_dist_erp=",I1)   

*
************************************************************************
*     tvfmfs_metric and itplv are the subroutines particularly needed to
*     predict contour distances for FM and analog (NTSC) TV
*     F(50,50) service and F(50,10) interfering contours.

      if(prop_curve .eq. 0 .or. prop_curve .eq. 1) then

         call tvfmfs_metric ( erpx, haatx, ichan, field, distance,
     &                        fs_or_dist, prop_curve, flag )

************************************************************************
*     Digital TV propagation curves F(50,90)

      else if(prop_curve.eq.2) then
      
	   call f5090 ( erpx, haatx, ichan, field, distance,
     &                        fs_or_dist, flag )
     
 
      end if


************************************************************************
*     If we are finding the erp, calculate the power.                  *
************************************************************************
c
      if ( fs_dist_erp .eq. 3 ) then
c
         power_in = 10.0 ** (( field_for_erp - field ) / 10.0 )
         call round_power( power_in, power_out, error_flag )
         erp = power_out  ! kilowatts

	   if(erp .gt. 9999.00) then ! print ERP valid, error code A6
	      flag = 'A6'
	      erp = 0.0
         end if
c
         if ( power_unit .eq. 2 ) then ! convert to dBk
            erp = 10.0 * log10 ( erp )
            power_out = 10.0 * log10 ( power_in )  ! dBk = dB(kilowatts)
         end if

		 if(fs_unit.eq.2) then

		 end if
c
      end if
*
************************************************************************
*     Change tvfmfs arguments back to user inputs for printing.        *
************************************************************************
*
      if ( fs_dist_erp .eq. 3 ) field = field_for_erp
c
      if ( fs_unit .eq. 2 ) field = 1.E-3 * 10. ** ( field / 20. )
      if ( mikm .eq. 'mi' ) distance = distance / 1.609344
*
************************************************************************
*     Set any flag message from tvfmfs.                                *
************************************************************************
*
      if ( flag .eq. '  ' ) then
         flag_message = ' '
      else if ( flag .eq. 'A1' ) then
         flag_message = 'Free Space equation used.'
      else if ( flag .eq. 'A2' ) then
         flag_message = 'Distance exceeds greatest curve value.'
      else if ( flag .eq. 'A3' ) then
         flag_message = 'Invalid Channel Number.'
      else if ( flag .eq. 'A4' ) then
         flag_message = 'Invalid curve selection.'
      else if ( flag .eq. 'A5' ) then
         flag_message = 'Invalid output switch value.'
      else if ( flag .eq. 'A6' ) then
         flag_message = 'Invalid erp value.'
	   erp = 0.0
	   erpx = 0.0
	   power_in = 0.0
      else if ( flag .eq. 'A7' ) then
         flag_message = 'HAAT less than 30 meters, used 30 meters.'
      else if ( flag .eq. 'A8' ) then
         flag_message = 'HAAT exceeds 1600 meters, used 1600 meters.'
      else if ( flag .eq. 'A9' ) then
         flag_message = 'Invalid distance for finding field strength.'
	   distance = 0.0
      else
         flag_message = ' '
      end if
*
************************************************************************
*     Print the results to the console application                     *
************************************************************************
*
      write ( 6, 132 ) curvs(prop_curve+1), flag_message, erp,
     &                 aerp(power_unit), haat, ahaat,
     &                 aservice(service)

      if(save.eq.1) then
         write ( 7, 132 ) curvs(prop_curve+1), flag_message, erp,
     &                 aerp(power_unit), haat, ahaat,
     &                 aservice(service)
      end if


 132  format (/ '  F(50,', A2, ') curves     ', A /
     &         '  ERP =', F9.3, '(', a , ')  HAAT =', F9.1, '(', A2,
     &         ')   ', a19 )

      if(service .le. 3) then ! FM, NTSC TV
	    write ( 6, 138 ) field, inx(fs_unit), distance, mikm
        if(save.eq.1) write (7, 138) field, inx(fs_unit), distance, mikm
      else if(service .ge. 4) then ! Digital TV
	    call round(field, 0.01)
	    write ( 6, 238 ) field, inx(fs_unit), distance, mikm
        if(save.eq.1) then
		  write (7, 238) field, inx(fs_unit), distance, mikm
        end if
        ! DTV limited to one place to the right of the decimal to maintain
        ! consistency with the FCC's internal CDBS implementation.
      end if

 138  format ( '  Field Strength = ', G12.5, '(', a , ')  Dist =',
     &         F10.3, '(', a2, ')', /)


 238  format ( '  Field Strength = ', G12.5, '(', a , ')  Dist =',
     &         F10.3, '(', a2, ')', /)


c
      if ( fs_dist_erp .eq. 3 ) then
        write ( 6, 134 ) power_in, aerp(power_unit )
	  if(save.eq.1) write ( 7, 134 ) power_in, aerp(power_unit )
 134    format ( '  Unrounded ERP = ', f9.3, '(', a , ')' )
        if(power_in.ge.100.50000) write(6,135)
        if(save.eq.1) write(7,135)
 135    format("  ERP exceeds 100 kW (20 dBk) maximum permitted for FM s
     &tations in the USA!"/)
      end if


*
************************************************************************
*     Reset some default values.                                       *
************************************************************************
*
      if ( fs_dist_erp .eq. 1 ) then
         field    = 60.0
         field_in = '60'
      else if ( fs_dist_erp .eq. 2 ) then
         distance = 100.0
         dist_in  = '100'
      else if ( fs_dist_erp .eq. 3 ) then
         erp = 1.0
         erpx = erp
         erp_in = '1.0'
      end if
*
************************************************************************
*     Recycle to get the next value.                                   *
************************************************************************
*
      GO TO 40
*
************************************************************************
*     Terminate program.                                               *
************************************************************************
*
900   call exit
*
      end
