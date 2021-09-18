import cv2
import numpy as np


def detection(org,img):
  h,w,_ = img.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  bl,gl,rl = cv2.split(org)
  bf,gf,rf = cv2.split(org)
  b,g,r = cv2.split(org)
  _lnd,_fld = np.full((h,w), 255),np.full((h,w), 255)
  _det = np.full((h,w), 255)

  # dummy = np.loadtxt('results/dummy.txt').astype(np.uint16)
  # label = np.loadtxt('results/label.txt').astype(np.uint16)

  lab,hsv = cv2.cvtColor(img,cv2.COLOR_BGR2Lab),cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#   _dis = cv2.imread('results/tex/dissimilarity.png', cv2.IMREAD_COLOR)
  _edge = cv2.imread('results/edge/canny.png', cv2.IMREAD_COLOR)


  Lp,ap,bp = cv2.split(lab)
  hp,sp,vp = cv2.split(hsv)

  _landslide = (Lp>128)&(ap>128)
  landslide = _landslide

  _flooded = (Lp>135)&(ap>128)
  flooded = _flooded

  idx = np.where(_landslide)
  bl[idx],gl[idx],rl[idx] = (bo[idx]*al+100*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+230*(1-al))
  bf[idx],gf[idx],rf[idx] = (bo[idx]*al+90*(1-al)),(go[idx]*al+230*(1-al)),(ro[idx]*al+250*(1-al))


  lnd,fld = np.dstack((np.dstack((bl,gl)),rl)),np.dstack((np.dstack((bf,gf)),rf))

  cv2.imwrite('results/mask/_landslide.png', _lnd)
  cv2.imwrite('results/mask/_flooded.png', _fld)
  cv2.imwrite('results/mask/_detection.png', _det)
  cv2.imwrite('results/landslide.png', lnd)
  cv2.imwrite('results/flooded.png', fld)

  return _lnd,_fld



def rejection(org,img):
  h,w,_ = img.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  bs,gs,rs = cv2.split(org)
  bv,gv,rv = cv2.split(org)
  br,gr,rr = cv2.split(org)
  bb,gb,rb = cv2.split(org)
  b,g,r = cv2.split(org)
  _sky,_veg = np.full((h,w), 255),np.full((h,w), 255)
  _rbl,_bld = np.full((h,w), 255),np.full((h,w), 255)
  _rej = np.full((h,w), 255)

  lab,hsv = cv2.cvtColor(img,cv2.COLOR_BGR2Lab),cv2.cvtColor(img,cv2.COLOR_BGR2HSV)



  Lp,ap,bp = cv2.split(lab)
  hp,sp,vp = cv2.split(hsv)
  _bo,_go,_ro = cv2.split(org)

  # 空
  sky = (Lp>=200)&(bp<=135)&(ap>=125)
  # 植生
  _vegitation = ((ap<120)|(bp<120))&(hp>20)
  vegitation = _vegitation&(~sky)
  # # 瓦礫
  # # dis = np.split(_dis[idx],3,axis=1)[0]
  # edge = np.split(_edge[idx],3,axis=1)[0]
  # if ((np.count_nonzero(dummy==l))!=0):
  #   ep = (np.count_nonzero(edge>150))/(np.count_nonzero(dummy==l))
  # else:
  #   ep = 0
  # # rubble = (gsi>0.5)&(dis>0.8)
  # rubble = (ep>0.35)
  # 建物（形状特徴と直線のやつはじきたかった）
  # L,S = 0,np.count_nonzero(dm==l)
  # irr = L**2/(4*np.pi*S)
  # _ro[np.where((_ro+_bo+_go)==0)] = 1
  # gsi = ((_ro-_bo))/(_ro+_bo+_go)
  # _building = (gsi<0.15)
  # building = (_building)&(~sky)&(~vegitation)

  idx = np.where(_vegitation)

  bv[idx],gv[idx],rv[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  b[idx],g[idx],r[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  _veg[idx],_rej[idx] = 0,0

  # if (np.count_nonzero(sky)>np.count_nonzero(~sky)):
  #   bs[idx],gs[idx],rs[idx] = (bo[idx]*al+220*(1-al)),(go[idx]*al+190*(1-al)),(ro[idx]*al+40*(1-al))
  #   b[idx],g[idx],r[idx] = (bo[idx]*al+220*(1-al)),(go[idx]*al+190*(1-al)),(ro[idx]*al+40*(1-al))
  #   _sky[idx],_rej[idx] = 0,0
  # if (np.count_nonzero(vegitation)>np.count_nonzero(~vegitation)):
  #   bv[idx],gv[idx],rv[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  #   b[idx],g[idx],r[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  #   _veg[idx],_rej[idx] = 0,0
  # # if (np.count_nonzero(rubble)>np.count_nonzero(~rubble)):
  # if (rubble):
  #   br[idx],gr[idx],rr[idx] = (bo[idx]*al+30*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+250*(1-al))
  #   b[idx],g[idx],r[idx] = (bo[idx]*al+0*(1-al)),(go[idx]*al+150*(1-al)),(ro[idx]*al+250*(1-al))
  #   _rbl[idx],_rej[idx] = 0,0
  # if (np.count_nonzero(building)>np.count_nonzero(~building)):
  #   bb[idx],gb[idx],rb[idx] = (bo[idx]*al+200*(1-al)),(go[idx]*al+130*(1-al)),(ro[idx]*al+150*(1-al))
  #   b[idx],g[idx],r[idx] = (bo[idx]*al+200*(1-al)),(go[idx]*al+130*(1-al)),(ro[idx]*al+150*(1-al))
  #   _bld[idx],_rej[idx] = 0,0

  sky,veg = np.dstack((np.dstack((bs,gs)),rs)),np.dstack((np.dstack((bv,gv)),rv))
  # rbl,bld = np.dstack((np.dstack((br,gr)),rr)),np.dstack((np.dstack((bb,gb)),rb))
  # rej = np.dstack((np.dstack((b,g)),r))

  cv2.imwrite('results/mask/_sky.png', _sky)
  cv2.imwrite('results/mask/_vegitation.png', _veg)
  cv2.imwrite('results/mask/_rubble.png', _rbl)
  cv2.imwrite('results/mask/_building.png', _bld)
  cv2.imwrite('results/mask/_rejection.png', _rej)
  cv2.imwrite('results/sky.png', sky)
  cv2.imwrite('results/vegitation.png', veg)
  # cv2.imwrite('results/rubble.png', rbl)
  # cv2.imwrite('results/building.png', bld)
  # cv2.imwrite('results/rejection.png', rej)

  return _rej,_sky,_veg,_rbl,_bld
