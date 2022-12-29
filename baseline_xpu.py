import torch
import time
import sys

 
if len(sys.argv) > 2:
    print("A single file name is required")
    exit()
filename = sys.argv[1]
     

coef3rdOrder = 0.2500

# Reading data from file
input_data_file = open(filename, 'r')
Lines = input_data_file.readlines()
nVertLevels  = int(Lines[1].strip())
nCellsAll    = int(Lines[3].strip())
nCellsAll2   = int(Lines[5].strip())
nEdgesAll    = int(Lines[7].strip())
nTracers     = int(Lines[9].strip())



line_count = 11
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
lt3 = int(Lines[line_count+2].strip())
tracers = [0.0 for x in range(lt1*lt2*lt3)]
line_count += 3
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2*lt3]:
    tracers[read_count] = float(line.strip())
    read_count += 1

tracersT = torch.tensor(tracers)
tracersT = tracersT.reshape(lt1,lt2,lt3)
 


line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
normalThicknessFlux = [0.0 for x in range(lt1*lt2)]
line_count += 2 
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    normalThicknessFlux[read_count] = float(line.strip())
    read_count += 1

normalThicknessFluxT = torch.tensor(normalThicknessFlux)
normalThicknessFluxT = normalThicknessFluxT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
w = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    w[read_count] = float(line.strip())
    read_count += 1

wT = torch.tensor(w)
wT = wT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
layerThickness = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    layerThickness[read_count] = float(line.strip())
    read_count += 1

layerThicknessT = torch.tensor(layerThickness)
layerThicknessT = layerThicknessT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
lt3 = int(Lines[line_count+2].strip())
tend = [0.0 for x in range(lt1*lt2*lt3)]
line_count += 3
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2*lt3]:
    tend[read_count] = float(line.strip())
    read_count += 1

tendT = torch.tensor(tend)
tendT = tendT.reshape(lt1,lt2,lt3)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
advCellsForEdge = [0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    advCellsForEdge[read_count] = int(line.strip())
    read_count += 1

advCellsForEdgeT = torch.tensor(advCellsForEdge)
advCellsForEdgeT = advCellsForEdgeT.reshape(lt1,lt2)
advCellsForEdgeT = advCellsForEdgeT - 1   # python arrar indexing starts from 0



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
advCoefs = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    advCoefs[read_count] = float(line.strip())
    read_count += 1

advCoefsT = torch.tensor(advCoefs)
advCoefsT = advCoefsT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
advCoefs3rd = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    advCoefs3rd[read_count] = float(line.strip())
    read_count += 1

advCoefs3rdT = torch.tensor(advCoefs3rd)
advCoefs3rdT = advCoefs3rdT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
advMaskHighOrder = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    advMaskHighOrder[read_count] = float(line.strip())
    read_count += 1

advMaskHighOrderT = torch.tensor(advMaskHighOrder)
advMaskHighOrderT = advMaskHighOrderT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
cellsOnEdge = [0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    cellsOnEdge[read_count] = int(line.strip())
    read_count += 1

cellsOnEdgeT = torch.tensor(cellsOnEdge)
cellsOnEdgeT = cellsOnEdgeT.reshape(lt1,lt2)
cellsOnEdgeT = cellsOnEdgeT - 1 # python indexing starts from 0


line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
areaCell = [0.0 for x in range(lt1)]
line_count += 1
read_count = 0
for line in Lines[line_count:line_count+lt1]:
    areaCell[read_count] = float(line.strip())
    read_count += 1

areaCellT = torch.tensor(areaCell)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
dvEdge = [0.0 for x in range(lt1)]
line_count += 1
read_count = 0
for line in Lines[line_count:line_count+lt1]:
    dvEdge[read_count] = float(line.strip())
    read_count += 1

dvEdgeT = torch.tensor(dvEdge)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
edgeSignOnCell = [0.0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    edgeSignOnCell[read_count] = float(line.strip())
    read_count += 1

edgeSignOnCellT = torch.tensor(edgeSignOnCell)
edgeSignOnCellT = edgeSignOnCellT.reshape(lt1,lt2)



line_count += read_count + 1
lt1 = int(Lines[line_count].strip())
lt2 = int(Lines[line_count+1].strip())
edgesOnCell = [0 for x in range(lt1*lt2)]
line_count += 2
read_count = 0
for line in Lines[line_count:line_count+lt1*lt2]:
    edgesOnCell[read_count] = int(line.strip())
    read_count += 1

edgesOnCellT = torch.tensor(edgesOnCell)
edgesOnCellT = edgesOnCellT.reshape(lt1,lt2)
edgesOnCellT = edgesOnCellT - 1 # python indexing starts from 0



# Init tensors
vertFlxT = torch.zeros((nTracers,nVertLevels+1,nCellsAll),dtype=torch.float32)
highOrderFlxHorzT = torch.zeros((nTracers,nVertLevels,nEdgesAll),dtype=torch.float32)
nbrCellsT = torch.zeros(nTracers,nVertLevels,nEdgesAll,2)  # Each edge has 2 cells sharing this edge
advCellsT = torch.zeros(nTracers,nVertLevels,nEdgesAll,10)  # Each edge has 10 neighboring cells
nbrEdgesT = torch.zeros(nTracers,nVertLevels,nCellsAll,6)  # Each cell has 6 edges


# Move data to device
device = 'cuda:0'
torch.cuda.synchronize()
t_start = time.perf_counter()
tracersT              = tracersT.to(device)
normalThicknessFluxT  = normalThicknessFluxT.to(device)
wT                    = wT.to(device)
layerThicknessT       = layerThicknessT.to(device)
tendT                 = tendT.to(device)
advCellsForEdgeT      = advCellsForEdgeT.to(device)
advCoefsT             = advCoefsT.to(device)
advCoefs3rdT          = advCoefs3rdT.to(device)
advMaskHighOrderT     = advMaskHighOrderT.to(device)
cellsOnEdgeT          = cellsOnEdgeT.to(device)
areaCellT             = areaCellT.to(device)
dvEdgeT               = dvEdgeT.to(device)
edgeSignOnCellT       = edgeSignOnCellT.to(device)
edgesOnCellT          = edgesOnCellT.to(device)
vertFlxT              = vertFlxT.to(device)
highOrderFlxHorzT     = highOrderFlxHorzT.to(device)
nbrCellsT             = nbrCellsT.to(device)
advCellsT             = advCellsT.to(device)
nbrEdgesT             = nbrEdgesT.to(device)
torch.cuda.synchronize()
t_finish = time.perf_counter()
t7 = t_finish - t_start



# Vertical flux computation, interior layers
t_start = time.perf_counter()
kmin = 1 - 1 + 2                   # depth starts at 1, python array indexing from 0 (minus 1), interior layers offset (plus 2)
kmax = nVertLevels - 1 - 1 + 2 - 1 # depth starts at 1, python array indexing from 0 (minus 1), interior layers offset (plus 2), one less in tensor indexing (minus 1)
a=torch.broadcast_to(wT[kmin:kmax,:],(nTracers,-1,-1))
b=7.0*(tracersT[:,kmin:kmax,:nCellsAll]+tracersT[:,kmin-1:kmax-1,:nCellsAll])-(tracersT[:,kmin+1:kmax+1,:nCellsAll]+tracersT[:,kmin-2:kmax-2,:nCellsAll])
c=torch.broadcast_to(coef3rdOrder * abs(wT[kmin:kmax,:]),(nTracers,-1,-1))
d=tracersT[:,kmin+1:kmax+1,:nCellsAll] - tracersT[:,kmin-2:kmax-2,:nCellsAll]-3.0*(tracersT[:,kmin:kmax,:nCellsAll]-tracersT[:,kmin-1:kmax-1,:nCellsAll]) 
vertFlxT[:,kmin:kmax,:] =  (a * b - c * d) / 12.0
t_finish = time.perf_counter()
t1 = t_finish - t_start



# Vertical flux computation, edge layers
t_start = time.perf_counter()
k = kmin - 2 + 1
verticalWeightKT   = layerThicknessT[k-1,:] / (layerThicknessT[k,:] + layerThicknessT[k-1,:])
verticalWeightKm1T = 1 - verticalWeightKT
vertFlxT[:,k:k+1,:] = torch.broadcast_to(wT[k:k+1,:],(nTracers,-1,-1)) * (verticalWeightKT * tracersT[:,k:k+1,:nCellsAll] + verticalWeightKm1T * tracersT[:,k-1:k,:nCellsAll])
k = kmax
verticalWeightKT   = layerThicknessT[k-1,:] / (layerThicknessT[k,:] + layerThicknessT[k-1,:])
verticalWeightKm1T = 1 - verticalWeightKT
vertFlxT[:,k:k+1,:] = torch.broadcast_to(wT[k:k+1,:],(nTracers,-1,-1)) * (verticalWeightKT * tracersT[:,k:k+1,:nCellsAll] + verticalWeightKm1T * tracersT[:,k-1:k,:nCellsAll])
t_finish = time.perf_counter()
t2 = t_finish - t_start



# Vertical flux accumulation
t_start = time.perf_counter()
kmin = 1 - 1
kmax = nVertLevels - 1
vertDivFactor = 1.0
tendT[:,:,:nCellsAll] += vertDivFactor * (vertFlxT[:,kmin+1:kmax+2,:]-vertFlxT[:,kmin:kmax+1,:])
t_finish = time.perf_counter()
t3 = t_finish - t_start



# Horizontal flux computation, 2nd order
t_start = time.perf_counter()
tracerWgtT = (1.0-advMaskHighOrderT[:,:])*normalThicknessFluxT[:,:] * torch.broadcast_to((dvEdgeT[:] * 0.5), (nVertLevels,-1))
#nbrCellsT = torch.zeros(nTracers,nVertLevels,nEdgesAll,2)
for i in range(nEdgesAll):
  for j in range(nVertLevels):
    nbrCellsT[:,j,i,:] = tracersT[:,j,cellsOnEdgeT[i,:]]
highOrderFlxHorzT += tracerWgtT * (nbrCellsT[:,:,:,0] + nbrCellsT[:,:,:,1])
t_finish = time.perf_counter()
t4 = t_finish - t_start



# Horizontal flux computation, 3rd order
t_start = time.perf_counter()
tracerWgtT = torch.broadcast_to((advMaskHighOrderT*normalThicknessFluxT).unsqueeze(-1),(-1,-1,10)) * \
            (torch.broadcast_to(advCoefsT,(nVertLevels,-1,-1)) + \
             torch.broadcast_to((coef3rdOrder*torch.sign(normalThicknessFluxT)).unsqueeze(-1),(-1,-1,10)) * \
             torch.broadcast_to(advCoefs3rdT,(nVertLevels,-1,-1)))
# TO-DO: indexing optimization
for i in range(nEdgesAll):
  for j in range(nVertLevels):
    advCellsT[:,j,i,:] = tracersT[:,j,advCellsForEdgeT[i,:]]
highOrderFlxHorzT += torch.sum(tracerWgtT * advCellsT, 3)
t_finish = time.perf_counter()
t5 = t_finish - t_start



# Horizontal flux accumulation
t_start = time.perf_counter()
# TO-DO: indexing optimization
for i in range(nCellsAll):
  for j in range(nVertLevels):
    nbrEdgesT[:,j,i,:] = highOrderFlxHorzT[:,j,edgesOnCellT[i,:]]
tendT[:,:,:nCellsAll] += torch.sum(nbrEdgesT*edgeSignOnCellT,3)/areaCellT[:nCellsAll] 
t_finish = time.perf_counter()
t6 = t_finish - t_start



print("Vert flux computation  : ", t1+t2, " secs")
print("Vert flux accumulation : ", t3, " secs")
print("Horz flux computation  : ", t4+t5, " secs")
print("Horz flux accumulation : ", t6, " secs")
print("Data movement          : ", t7, " secs")
