import cv2
import numpy as np


def integration(mask,landslide,flooded,sky,veg,rbl,bld,org):
  h,w,_ = org.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  b,g,r = cv2.split(org)
  bn,gn,rn = cv2.split(org)
  ba,ga,ra = cv2.split(org)

  lnd,fld = np.full((h,w), 255),np.full((h,w), 255)

  # 斜面崩壊
  idx = np.where(landslide==0)
  b[idx],g[idx],r[idx] = (bo[idx]*al+100*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+230*(1-al))
  lnd[idx] = 0

  # 浸水
  idx = np.where(flooded==0)
  b[idx],g[idx],r[idx] = (bo[idx]*al+90*(1-al)),(go[idx]*al+230*(1-al)),(ro[idx]*al+250*(1-al))
  fld[idx] = 0

  # マスク処理（空・植生・瓦礫・建物）
  idx = np.where(mask==0)
  b[idx],g[idx],r[idx] = bo[idx],go[idx],ro[idx]
  lnd[idx],fld[idx] = 255,255

  # スライド画像用出力
  idx = np.where(sky==0)
  bn[idx],gn[idx],rn[idx] = (bo[idx]*al+220*(1-al)),(go[idx]*al+190*(1-al)),(ro[idx]*al+40*(1-al))
  idx = np.where(veg==0)
  bn[idx],gn[idx],rn[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  idx = np.where(rbl==0)
  ba[idx],ga[idx],ra[idx] = (bo[idx]*al+0*(1-al)),(go[idx]*al+150*(1-al)),(ro[idx]*al+250*(1-al))
  idx = np.where(bld==0)
  ba[idx],ga[idx],ra[idx] = (bo[idx]*al+200*(1-al)),(go[idx]*al+130*(1-al)),(ro[idx]*al+150*(1-al))

  
  res = np.dstack((np.dstack((b,g)),r))
  nature = np.dstack((np.dstack((bn,gn)),rn))
  artifact = np.dstack((np.dstack((ba,ga)),ra))

  cv2.imwrite('results/result.png', res)
  cv2.imwrite('results/nature.png', nature)
  cv2.imwrite('results/artifact.png', artifact)
  return lnd,fld


def evaluation(_lnd,_fld):
  lnd = np.dstack((np.dstack((_lnd,_lnd)),_lnd))
  fld = np.dstack((np.dstack((_fld,_fld)),_fld))
  ans = cv2.imread('images/answer1.png', cv2.IMREAD_COLOR)
  # ans = cv2.imread('images/answer2_.png', cv2.IMREAD_COLOR)
  
  # 斜面崩壊
  tp = np.count_nonzero((lnd==0)&(ans==(100,70,230)))
  fp = np.count_nonzero((lnd==0)&(ans!=(100,70,230)))
  fn = np.count_nonzero((lnd!=0)&(ans==(100,70,230)))
  print('landslide evaluation')
  precicsion = tp/(tp+fp)
  print('\tprecicsion :','{:.3g}'.format(precicsion))
  recall = tp/(tp+fn)
  print('\trecall :','{:.3g}'.format(recall))
  f1 = 2*(recall*precicsion)/(recall+precicsion)
  print('\tf1-measure :','{:.3g}'.format(f1))

  # 浸水
  tp = np.count_nonzero((fld==0)&(ans==(90,230,250)))
  fp = np.count_nonzero((fld==0)&(ans!=(90,230,250)))
  fn = np.count_nonzero((fld!=0)&(ans==(90,230,250)))
  print('flooded evaluation')
  precicsion = tp/(tp+fp)
  print('\tprecicsion :','{:.3g}'.format(precicsion))
  recall = tp/(tp+fn)
  print('\trecall :','{:.3g}'.format(recall))
  f1 = 2*(recall*precicsion)/(recall+precicsion)
  print('\tf1-measure :','{:.3g}'.format(f1))
