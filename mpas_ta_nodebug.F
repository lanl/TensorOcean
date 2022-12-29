      program ocn_tracer_advection_std

      implicit none

      !integer, parameter :: RKIND  = selected_real_kind(6)
      integer, parameter :: RKIND  = kind(1.)

      ! private module variables
      real (kind=RKIND) ::  coef3rdOrder       !< coefficient for blending high-order terms


!***********************************************************************
!
!  routine ocn_tracer_advection_std_tend
!
!> \brief MPAS standard tracer advection tendency
!> \author Doug Jacobsen
!> \date   03/09/12
!> \details
!>  This routine computes the standard tracer advection tendencity.
!>  Both horizontal and vertical.
!
!-----------------------------------------------------------------------

      !-----------------------------------------------------------------
      ! Input/Output variables
      !-----------------------------------------------------------------

      real (kind=RKIND), dimension(:,:,:), pointer :: &
         tend            !< [inout] Accumulated tracer tendency

      !-----------------------------------------------------------------
      ! Input variables
      !-----------------------------------------------------------------

      real (kind=RKIND), dimension(:,:,:), pointer :: &
         tracers               !< [in] current tracer values

      real (kind=RKIND), dimension(:,:), pointer :: &
         normalThicknessFlux, &!< [in] Thickness weighted velocitiy
         w,                   &!< [in] Vertical velocity
         layerThickness        !< [in] Thickness

      !-----------------------------------------------------------------
      ! Li: Read data
      !-----------------------------------------------------------------

      character (len = 20) :: name
      integer :: lt1, lt2, lt3
      integer, parameter :: u=5

      character (len = 20) :: arg
      integer :: stat

      !-----------------------------------------------------------------
      ! Localized external variables
      !-----------------------------------------------------------------

      integer, dimension(:,:), allocatable :: &
      advCellsForEdge      ! index of cells contributing to advection at edge

      real (kind=RKIND), dimension(:,:), allocatable :: &
      advCoefs,           &! common advection coefficients
      advCoefs3rd,        &! common advection coeffs for high order
      advMaskHighOrder     ! mask for high order advection terms

      real(kind=RKIND), dimension(:), pointer :: &
      areaCell,           &! area of each cell
      dvEdge               ! length of edge = dist between vertices along edge

      real(kind=RKIND), dimension(:, :), allocatable :: &
      edgeSignOnCell       ! sign of edge contributions to a cell

      integer, dimension(:, :), pointer :: &
      cellsOnEdge,        &! index of cells connected to each edge
      edgesOnCell          ! index of edges connected to each cell

      integer :: nVertLevels, nCellsAll, nCellsAll2, nEdgesAll, nCellsOwned



      integer :: vertOrder   !< choice of order for vertical advection
      integer, parameter :: &! enumerator for supported vertical adv order
         vertOrder2=2,      &!< 2nd order
         vertOrder3=3,      &!< 3rd order
         vertOrder4=4        !< 4th order

      !real (kind=RKIND), dimension(:,:), pointer :: &
      !   tracer          !< [in] current tracer values

      !real (kind=RKIND), dimension(:,:), pointer :: &
      !   layerThick      !< [in] Layer thickness to use for advection

      real (kind=RKIND) :: &
         verticalWeightK,  &! weights for vertical advection
         verticalWeightKm1  ! weights for vertical advection

      real (kind=RKIND), dimension(:,:), pointer :: &
         vertFlx         !< [out] high-order vertical advection flux

      !-----------------------------------------------------------------
      ! Local variables
      !-----------------------------------------------------------------

      integer :: &
         i, j, k,      &! loop indices for neighbors, vertical
         kmin, kmax,   &! min, max active vertical layers
         iCell, iEdge, &! loop indices for cells, edges
         iTracer,      &! tracer index
         cell1, cell2, &! neighbor cell indices across edge
         numTracers

      real (kind=RKIND) :: &
         tracerWgt,        &! local temporary
         invAreaCell1,     &! inverse cell area
         vertDivFactor      ! vertical divergence factor

      real (kind=RKIND), dimension(:,:), allocatable :: &
         tracerCur,        &! reordered tracer at current time
         highOrderFlxHorz, &! high-order flux in horizontal
         highOrderFlxVert   ! high-order flux in vertical

      integer(8) :: clock_start, clock_end, clock_rate
      integer(8) :: clock_start2, clock_end2
      real(kind=8) :: elapsed_time1=0, elapsed_time2=0, &
                          elapsed_time3=0, elapsed_time4=0, &
                          elapsed_time5=0, elapsed_time6=0, &
                          elapsed_time7=0, elapsed_time8=0 
      call system_clock(count_rate=clock_rate)

      ! End preamble
      !-----------------------------------------------------------------
      ! Begin code


      if (command_argument_count() .ne. 1) then
        write (*,*) 'A single input filename is required'
        stop
      end if
      call get_command_argument(1, arg)
      open (u, file = arg, iostat=stat, status = 'old')
      if (stat .ne. 0) then    
        write(*,*) arg, " cannot be opened"
        stop
      end if
 
      read(u,*) name
      read(u,*) nVertLevels
      read(u,*) name
      read(u,*) nCellsAll
      read(u,*) name
      read(u,*) nCellsAll2
      read(u,*) name
      read(u,*) nEdgesAll
      read(u,*) name
      read(u,*) numTracers

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      read(u,*) lt3
      allocate(tracers(lt1, lt2, lt3))
      do i = 1, lt1
        do j = 1, lt2
          do k = 1, lt3
            read(u,*) tracers(i, j, k)
          end do
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(normalThicknessFlux(lt1, lt2))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) normalThicknessFlux(i, j)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(w(lt1, lt2))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) w(i, j)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(layerThickness(lt1, lt2))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) layerThickness(i, j)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      read(u,*) lt3
      allocate(tend(lt1, lt2, lt3))
      do i = 1, lt1
        do j = 1, lt2
          do k =1, lt3
            read(u,*) tend(i, j, k)
          end do
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(advCellsForEdge(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) advCellsForEdge(j, i)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(advCoefs(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) advCoefs(j, i)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(advCoefs3rd(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) advCoefs3rd(j, i)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(advMaskHighOrder(lt1, lt2))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) advMaskHighOrder(i, j)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(cellsOnEdge(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) cellsOnEdge(j, i)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      allocate(areaCell(lt1))
      do i = 1, lt1
        read(u,*) areaCell(i)
      end do

      read(u,*) name
      read(u,*) lt1
      allocate(dvEdge(lt1))
      do i = 1, lt1
        read(u,*) dvEdge(i)
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(edgeSignOnCell(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) edgeSignOnCell(j, i)
        end do
      end do

      read(u,*) name
      read(u,*) lt1
      read(u,*) lt2
      allocate(edgesOnCell(lt2, lt1))
      do i = 1, lt1
        do j = 1, lt2
          read(u,*) edgesOnCell(j, i)
        end do
      end do


      close(u)

      coef3rdOrder = 0.2500000

      ! Allocate some arrays
      allocate(tracerCur       (nVertLevels  , nCellsAll2), &
               highOrderFlxHorz(nVertLevels  , nEdgesAll), &
               highOrderFlxVert(nVertLevels+1, nCellsAll))

      call system_clock(count=clock_start2)
      !$acc enter data &
      !$acc    create(tracerCur, highOrderFlxHorz, highOrderFlxVert) &
      !$acc    copyin(tracers, w, layerthickness, tend, &
      !$acc          advCellsForEdge, advCoefs, advCoefs3rd, &
      !$acc          advMaskHighOrder, cellsOnEdge, dvEdge, &
      !$acc          normalThicknessFlux, areaCell, &
      !$acc          edgeSignOnCell, edgesOnCell, coef3rdOrder)
      call system_clock(count=clock_end2)
      elapsed_time6 = real((clock_end2-clock_start2),kind=8) / &
                      real(clock_rate,kind=8)      

      ! Loop over tracers. One tracer is advected at a time. It is
      ! copied into a temporary array in order to improve locality
      do iTracer = 1, numTracers
        ! Initialize variables for use in this iTracer iteration
#ifdef MPAS_OPENACC
        !$acc parallel loop collapse(2) &
        !$acc    present(tracerCur, tracers)
#else
        !$omp parallel
        !$omp do schedule(runtime) private(k)
#endif
        do iCell = 1, nCellsAll2
        do k=1,nVertLevels
           tracerCur(k,iCell) = tracers(iTracer,k,iCell)
        end do
        end do
#ifndef MPAS_OPENACC
        !$omp end do
#endif

#ifdef MPAS_OPENACC
        !$acc parallel loop collapse(2) &
        !$acc    present(highOrderFlxHorz)
#else
        !$omp do schedule(runtime) private(k)
#endif
        do iEdge = 1, nEdgesAll
        do k=1,nVertLevels
           highOrderFlxHorz(k, iEdge) = 0.0_RKIND
        end do
        end do
#ifndef MPAS_OPENACC
        !$omp end do
#endif
      

#ifdef MPAS_OPENACC
      !$acc parallel loop collapse(2) present(highOrderFlxVert)
#else
      !$omp parallel
      !$omp do schedule(runtime) private(k)
#endif
      do iCell = 1, nCellsAll
      do k=1,nVertLevels+1
         highOrderFlxVert(k,iCell) = 0.0_RKIND
      end do
      end do
#ifndef MPAS_OPENACC
      !$omp end do
#endif


        ! Compute the high order vertical flux.



        ! Compute flux for interior layers at high order based on
        ! user-requested order


        kmin = 1 
        kmax = nVertLevels

         call system_clock(count=clock_start)
#ifdef MPAS_OPENACC
         !$acc parallel loop &
         !$acc    present(w, &
         !$acc            highOrderFlxVert, tracerCur) &
         !$acc    private(k, kmin, kmax)
#else
         !$omp do schedule(runtime) &
         !$omp    private(k, kmin, kmax)
#endif
         do iCell = 1, nCellsAll
            do k=kmin+2,kmax-1
               highOrderFlxVert(k, iCell) = (w(k,iCell)* &
                                   (7.0_RKIND * (tracerCur(k  ,iCell)+ &
                                                 tracerCur(k-1,iCell)) - &
                                                (tracerCur(k+1,iCell)+ &
                                                 tracerCur(k-2,iCell))) - &
                                coef3rdOrder*abs(w(k,iCell))* &
                                               ((tracerCur(k+1,iCell)- &
                                                 tracerCur(k-2,iCell)) - &
                                      3.0_RKIND*(tracerCur(k  ,iCell)- &
                                                 tracerCur(k-1,iCell))))/ &
                                                 12.0_RKIND
            end do ! vertical loop
         end do ! iCell Loop
#ifndef MPAS_OPENACC
         !$omp end do
#endif
         call system_clock(count=clock_end)
         elapsed_time1 = elapsed_time1 + &
                      real((clock_end-clock_start),kind=8) / &
                      real(clock_rate,kind=8)

      ! Now take care of the edge cases, reducing order for
      ! layers near the top and bottom where high-order forms
      ! can not be computed.


      call system_clock(count=clock_start)
#ifdef MPAS_OPENACC
      !$acc parallel loop &
      !$acc    present(w, &
      !$acc            layerThickness, highOrderFlxVert, tracerCur) &
      !$acc    private(k, kmin, kmax, &
      !$acc            verticalWeightK, verticalWeightKm1)
#else
      !$omp do schedule(runtime) &
      !$omp    private(k, kmin, kmax, &
      !$omp            verticalWeightK, verticalWeightKm1)
#endif
      do iCell = 1, nCellsAll
         ! at top, flux is zero (already initialized)
         ! at next-to-top (kmin+1), reduce to 2nd order
         !   but avoid case where 0 or 1 active layer (kmax <= kmin)
         !if (kmax > kmin) then
            k = kmin+1
            verticalWeightK   = layerThickness(k-1,iCell) / &
                               (layerThickness(k  ,iCell) + &
                                layerThickness(k-1,iCell))
            verticalWeightKm1 = layerThickness(k  ,iCell) / &
                               (layerThickness(k  ,iCell) + &
                                layerThickness(k-1,iCell))
            highOrderFlxVert(k,iCell) = w(k,iCell)&
                          *(verticalWeightK  *tracerCur(k  ,iCell) + &
                            verticalWeightKm1*tracerCur(k-1,iCell))
            ! Deepest active level also at 2nd order
            k = kmax
            verticalWeightK   = layerThickness(k-1,iCell) / &
                               (layerThickness(k  ,iCell) + &
                                layerThickness(k-1,iCell))
            verticalWeightKm1 = layerThickness(k  ,iCell) / &
                               (layerThickness(k  ,iCell) + &
                                layerThickness(k-1,iCell))
            highOrderFlxVert(k,iCell) = w(k,iCell)* &
                          (verticalWeightK  *tracerCur(k  ,iCell) + &
                           verticalWeightKm1*tracerCur(k-1,iCell))
         !end if ! kmax > kmin
      end do ! iCell Loop
#ifndef MPAS_OPENACC
      !$omp end do
      !$omp end parallel
#endif
      call system_clock(count=clock_end)
      elapsed_time2 = elapsed_time2 + &
                      real((clock_end-clock_start),kind=8) / &
                      real(clock_rate,kind=8)
        
        ! Accumulate the scaled high order vertical tendencies.
        vertDivFactor = 1.0_RKIND

        call system_clock(count=clock_start)
#ifdef MPAS_OPENACC
        !$acc parallel loop &
        !$acc    present(tend, &
        !$acc            highOrderFlxVert) &
        !$acc    private(k, kmin, kmax)
#else
        !$omp do schedule(runtime) private(k, kmin, kmax)
#endif
        do iCell = 1, nCellsAll !nCellsOwned
           do k = kmin,kmax
              tend(iTracer, k, iCell) = tend(iTracer, k, iCell) + &
                         vertDivFactor*(highOrderFlxVert(k+1, iCell) &
                                      - highOrderFlxVert(k, iCell))
           end do ! k loop
        end do ! iCell loop
#ifndef MPAS_OPENACC
        !$omp end do
        !$omp end parallel
#endif
        call system_clock(count=clock_end)
        elapsed_time3 = elapsed_time3 + &
                      real((clock_end-clock_start),kind=8) / &
                      real(clock_rate,kind=8)


        ! Compute the high order horizontal flux

        call system_clock(count=clock_start)
#ifdef MPAS_OPENACC
        !$acc parallel loop &
        !$acc    present(cellsOnEdge, &
        !$acc            advCellsForEdge, dvEdge, &
        !$acc            advMaskHighOrder, advCoefs, advCoefs3rd, &
        !$acc            normalThicknessFlux, highOrderFlxHorz, &
        !$acc            tracerCur) &
        !$acc    private(i,iCell,cell1,cell2, k, kmin, kmax, tracerWgt) 
#else
        !$omp do schedule(runtime) &
        !$omp    private(i,iCell,cell1,cell2, k, kmin, kmax, tracerWgt) 
#endif
        do iEdge = 1, nEdgesAll
          cell1 = cellsOnEdge(1, iEdge)
          cell2 = cellsOnEdge(2, iEdge)
          ! Compute 2nd order fluxes where needed.
          do k = kmin, kmax
            tracerWgt = (1.0_RKIND - advMaskHighOrder(k,iEdge)) &
                      * (dvEdge(iEdge) * 0.5_RKIND) &
                      * normalThicknessFlux(k, iEdge)
            highOrderFlxHorz(k, iEdge) = highOrderFlxHorz(k, iedge) &
                                       + tracerWgt*(tracerCur(k,cell1) &
                                                  + tracerCur(k,cell2))
          end do ! k loop
          ! Compute 3rd or 4th fluxes where requested.
          do i = 1, 10 !nAdvCellsForEdge(iEdge)
            iCell = advCellsForEdge(i,iEdge)
            do k = kmin,kmax
              tracerWgt = advMaskHighOrder(k,iEdge) &
                        * (advCoefs(i,iEdge) + coef3rdOrder &
                        * sign(1.0_RKIND,normalThicknessFlux(k,iEdge)) &
                        * advCoefs3rd(i,iEdge))
              tracerWgt = normalThicknessFlux(k,iEdge)*tracerWgt  
              highOrderFlxHorz(k,iEdge) = highOrderFlxHorz(k,iEdge) &
                                        + tracerWgt*tracerCur(k,iCell)
            end do ! k loop
          end do ! i loop over nAdvCellsForEdge
        end do ! iEdge loop
#ifndef MPAS_OPENACC
        !$omp end do
#endif
        call system_clock(count=clock_end)
        elapsed_time4 = elapsed_time4 + &
                      real((clock_end-clock_start),kind=8) / &
                      real(clock_rate,kind=8)
        ! Accumulate the scaled high order horizontal tendencies


        call system_clock(count=clock_start)
#ifdef MPAS_OPENACC
        !$acc parallel loop &
        !$acc    present(edgesOnCell, edgeSignOnCell, &
        !$acc            areaCell, tend, highOrderFlxHorz) &
        !$acc    private(i, iEdge, k, kmin, kmax, invAreaCell1)
#else
        !$omp do schedule(runtime) &
        !$omp    private(i, iEdge, k, kmin, kmax, invAreaCell1)
#endif
        do iCell = 1, nCellsAll
          invAreaCell1 = 1.0_RKIND / areaCell(iCell)
          do i = 1, 6 !nEdgesOnCell(iCell)
            iEdge = edgesOnCell(i, iCell)
            do k = kmin,kmax
              tend(iTracer, k, iCell) = tend(iTracer, k, iCell) &
                                      + edgeSignOnCell(i, iCell) &
                                      * highOrderFlxHorz(k, iEdge) &
                                      * invAreaCell1
            end do
          end do
        end do
#ifndef MPAS_OPENACC
        !$omp end do
#endif
        call system_clock(count=clock_end)
        elapsed_time5 = elapsed_time5 + &
                      real((clock_end-clock_start),kind=8) / &
                      real(clock_rate,kind=8)


      end do ! iTracer loop

      !$acc exit data &
      !$acc    delete(tracerCur, highOrderFlxHorz, highOrderFlxVert, &
      !$acc          tracers, w, layerthickness, tend, &
      !$acc          advCellsForEdge, advCoefs, advCoefs3rd, &
      !$acc          advMaskHighOrder, cellsOnEdge, dvEdge, &
      !$acc          normalThicknessFlux, areaCell, &
      !$acc          edgeSignOnCell, edgesOnCell, coef3rdOrder)


      write(*,*) tend(1, 3, 10)

      deallocate(tracerCur, highOrderFlxHorz, highOrderFlxVert)

      print '("Vert flux computation  : ",f16.8," secs")',elapsed_time1 + elapsed_time2
      print '("Vert flux accumulation : ",f16.8," secs")',elapsed_time3
      print '("Horz flux computation  : ",f16.8," secs")',elapsed_time4
      print '("Horz flux accumulation : ",f16.8," secs")',elapsed_time5
      print '("Data movement          : ",f16.8," secs")',elapsed_time6



      end program ocn_tracer_advection_std

!|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
