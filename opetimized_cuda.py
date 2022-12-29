import torch
import time

N=1600
M=N+4
L=10
T=1


#tend            = torch.randn(T,L,N,N)
#tracers         = torch.randn(T,L,N,N)

edgeSignOnCell1 = torch.randn(1,N+1,N*2+1)
edgeSignOnCell2 = torch.randn(1,N,N+1)
areaCell        = torch.randn(N)
coef3rdOrder    = 0.250
dvEdge1         = torch.randn(1,N+1,N*2+1,1)
dvEdge2         = torch.randn(1,N,N+1,1)
advMaskHighOrder1 = torch.randn(L,N+1,N*2+1,1)
advMaskHighOrder2 = torch.randn(L,N,N+1,1)
advCoefs1         = torch.randn(1,N+1,N*2+1,10)
advCoefs2         = torch.randn(1,N,N+1,10)
advCoefs3rd1      = torch.randn(1,N+1,N*2+1,10)
advCoefs3rd2      = torch.randn(1,N,N+1,10)
normalThicknessFlux1 = torch.randn(L,N+1,N*2+1,1)
normalThicknessFlux2 = torch.randn(L,N,N+1,1)
cell = torch.randn(L,M,M)

EvenRow2_mask = torch.tensor([False,True,True,True,True,True,True,True,False,True,True,True])
OddRow2_mask = torch.tensor([True,True,True,False,True,True,True,True,True,True,True,False])
EvenRowEvenCol1_mask = torch.tensor([False,True,True,False,True,True,True,False,False,True,True,True,False,True,True,False])
EvenRowOddCol1_mask = torch.tensor([False,False,True,True,False,True,True,True,False,True,True,True,False,True,True,False])
OddRowEvenCol1_mask = torch.tensor([False,True,True,False,False,True,True,True,True,True,True,False,False,True,True,False])
OddRowOddCol1_mask = torch.tensor([False,True,True,False,False,True,True,True,False,True,True,True,False,False,True,True])


device = 'cuda:0'
torch.cuda.synchronize()
t2 = time.perf_counter()
edgeSignOnCell1      = edgeSignOnCell1.to(device)
edgeSignOnCell2      = edgeSignOnCell2.to(device)
areaCell             = areaCell.to(device)
#coef3rdOrder         = coef3rdOrder.to(device)
dvEdge1              = dvEdge1.to(device)
dvEdge2              = dvEdge2.to(device)
advMaskHighOrder1    = advMaskHighOrder1.to(device)
advMaskHighOrder2    = advMaskHighOrder2.to(device)
advCoefs1            = advCoefs1.to(device)
advCoefs2            = advCoefs2.to(device)
advCoefs3rd1         = advCoefs3rd1.to(device)
advCoefs3rd2         = advCoefs3rd2.to(device)
normalThicknessFlux1 = normalThicknessFlux1.to(device)
normalThicknessFlux2 = normalThicknessFlux2.to(device)
cell                 = cell.to(device)
EvenRow2_mask        = EvenRow2_mask.to(device)
OddRow2_mask         = OddRow2_mask.to(device)
EvenRowEvenCol1_mask = EvenRowEvenCol1_mask.to(device)
EvenRowOddCol1_mask  = EvenRowOddCol1_mask.to(device)
OddRowEvenCol1_mask  = OddRowEvenCol1_mask.to(device)
OddRowOddCol1_mask   = OddRowOddCol1_mask.to(device)
torch.cuda.synchronize()
t2 = time.perf_counter() - t2


t1 = time.perf_counter()
tracerWgt1=(torch.broadcast_to(advCoefs1, (L, -1, -1, -1))+torch.broadcast_to(torch.sign(normalThicknessFlux1)*coef3rdOrder, (L, -1, -1, -1)))*torch.broadcast_to(normalThicknessFlux1*advMaskHighOrder1 , (-1, -1, -1, 10)) * torch.broadcast_to(advCoefs3rd1, (L, -1, -1, -1))
tracerWgt2=(torch.broadcast_to(advCoefs2, (L, -1, -1, -1))+torch.broadcast_to(torch.sign(normalThicknessFlux2)*coef3rdOrder, (L, -1, -1, -1)))*torch.broadcast_to(normalThicknessFlux2*advMaskHighOrder2 , (-1, -1, -1, 10)) * torch.broadcast_to(advCoefs3rd2, (L, -1, -1, -1))

a = cell[:,1:cell.size(dim=1)-1,:].unfold(2,4,1)
b = torch.cat((a[:,0:a.size(dim=1)-2,:], a[:,1:a.size(dim=1)-1,:], a[:,2:a.size(dim=1),:]), 3)
EvenRow2_cells=b[:,::2,:,EvenRow2_mask]
OddRow2_cells=b[:,1::2,:,OddRow2_mask]
highOrderFlxHorz2_EvenRow = torch.sum(tracerWgt2[:,::2,:,:]*EvenRow2_cells, 3)
highOrderFlxHorz2_OddRow = torch.sum(tracerWgt2[:,1::2,:,:]*OddRow2_cells, 3)

a = cell.unfold(2,4,1)
b = torch.cat((a[:,0:a.size(dim=1)-3,:], a[:,1:a.size(dim=1)-2,:], a[:,2:a.size(dim=1)-1,:],  a[:,3:a.size(dim=1),:]), 3)
EvenRow = b[:,::2,:,:]
OddRow = b[:,1::2,:,:]
EvenRowEvenCol1_cells=EvenRow[:,:,:,EvenRowEvenCol1_mask]
EvenRowOddCol1_cells=EvenRow[:,:,:EvenRow.size(dim=2)-1,EvenRowOddCol1_mask]
OddRowEvenCol1_cells=OddRow[:,:,:,OddRowEvenCol1_mask]
OddRowOddCol1_cells=OddRow[:,:,:OddRow.size(dim=2)-1,OddRowOddCol1_mask]
highOrderFlxHorz1_EvenRowEvenCol = torch.sum(EvenRowEvenCol1_cells*tracerWgt1[:,::2,::2,:], 3)
highOrderFlxHorz1_EvenRowOddCol = torch.sum(EvenRowOddCol1_cells*tracerWgt1[:,::2,1::2,:], 3)
highOrderFlxHorz1_OddRowEvenCol = torch.sum(OddRowEvenCol1_cells*tracerWgt1[:,1::2,::2,:], 3)
highOrderFlxHorz1_OddRowOddCol = torch.sum(OddRowOddCol1_cells*tracerWgt1[:,1::2,1::2,:], 3)

##2nd order
tracerWgt1 = torch.broadcast_to(dvEdge1*0.500, (L,-1,-1,-1)) * torch.broadcast_to((1.000 - advMaskHighOrder1)*normalThicknessFlux1,(L,-1,-1,-1))
tracerWgt2 = torch.broadcast_to(dvEdge2*0.500, (L,-1,-1,-1)) * torch.broadcast_to((1.000 - advMaskHighOrder2)*normalThicknessFlux2,(L,-1,-1,-1))

EvenRow = cell[:,1:cell.size(dim=1)-1:2,1:cell.size(dim=2)-1]
OddRow = cell[:,2:cell.size(dim=1)-1:2,1:cell.size(dim=2)-1]

highOrderFlxHorz1_EvenRowEvenCol +=  (EvenRow[:,:highOrderFlxHorz1_EvenRowEvenCol.size(dim=1), :EvenRow.size(dim=2)-1] + OddRow[:,:highOrderFlxHorz1_EvenRowEvenCol.size(dim=1),1:]) * (tracerWgt1[:,::2,::2,:]).squeeze(-1)
highOrderFlxHorz1_EvenRowOddCol +=  (EvenRow[:,:highOrderFlxHorz1_EvenRowOddCol.size(dim=1),1:EvenRow.size(dim=2)-1] + OddRow[:,:highOrderFlxHorz1_EvenRowOddCol.size(dim=1),1:EvenRow.size(dim=2)-1]) * (tracerWgt1[:,::2,1::2,:]).squeeze(-1)
highOrderFlxHorz1_OddRowEvenCol += (EvenRow[:,1:1+highOrderFlxHorz1_OddRowEvenCol.size(dim=1),:EvenRow.size(dim=2)-1] + OddRow[:,:highOrderFlxHorz1_OddRowEvenCol.size(dim=1),1:]) * (tracerWgt1[:,1::2,::2,:]).squeeze(-1)
highOrderFlxHorz1_OddRowOddCol += (EvenRow[:,1:1+highOrderFlxHorz1_OddRowOddCol.size(dim=1),1:EvenRow.size(dim=2)-1] + OddRow[:,:highOrderFlxHorz1_OddRowOddCol.size(dim=1),1:EvenRow.size(dim=2)-1]) * (tracerWgt1[:,1::2,1::2,:]).squeeze(-1)

highOrderFlxHorz1_EvenRowEvenCol *= edgeSignOnCell1[:,::2,::2]
highOrderFlxHorz1_EvenRowOddCol *= edgeSignOnCell1[:,::2,1::2]
highOrderFlxHorz1_OddRowEvenCol *= edgeSignOnCell1[:,1::2,::2]
highOrderFlxHorz1_OddRowOddCol *= edgeSignOnCell1[:,1::2,1::2]
highOrderFlxHorz2_EvenRow *= edgeSignOnCell2[:,::2,:]
highOrderFlxHorz2_OddRow *= edgeSignOnCell2[:,1::2,:]



EvenRow_ = highOrderFlxHorz1_EvenRowEvenCol[:,:highOrderFlxHorz2_EvenRow.size(dim=1),:highOrderFlxHorz1_EvenRowOddCol.size(dim=2)] + highOrderFlxHorz1_EvenRowOddCol[:,:highOrderFlxHorz2_EvenRow.size(dim=1),:] + highOrderFlxHorz1_OddRowEvenCol[:,:,:highOrderFlxHorz1_EvenRowOddCol.size(dim=2)] + highOrderFlxHorz1_OddRowOddCol[:,:,:] + highOrderFlxHorz2_EvenRow[:,:,:highOrderFlxHorz2_EvenRow.size(dim=2)-1] + highOrderFlxHorz2_EvenRow[:,:,1:highOrderFlxHorz2_EvenRow.size(dim=2)]
EvenRow_ = EvenRow_/areaCell

OddRow_= highOrderFlxHorz1_EvenRowEvenCol[:,1:,:highOrderFlxHorz1_EvenRowOddCol.size(dim=2)] + highOrderFlxHorz1_EvenRowOddCol[:,1:,:] + highOrderFlxHorz1_OddRowEvenCol[:,:,:highOrderFlxHorz1_EvenRowOddCol.size(dim=2)] + highOrderFlxHorz1_OddRowOddCol[:,:,:] + highOrderFlxHorz2_OddRow[:,:,:highOrderFlxHorz2_OddRow.size(dim=2)-1] + highOrderFlxHorz2_OddRow[:,:,1:highOrderFlxHorz2_OddRow.size(dim=2)]
OddRow_ = OddRow_/areaCell


t1 = time.perf_counter() - t1

print("Time:   ",t1," secs")
print("Upload: ",t2," secs")
