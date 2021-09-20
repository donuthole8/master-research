import cv2
import numpy as np


def detection(org,img):
  h,w,_ = img.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  bl,gl,rl = cv2.split(org)
  _lnd = np.full((h,w), 255)

  lab,hsv = cv2.cvtColor(img,cv2.COLOR_BGR2Lab),cv2.cvtColor(img,cv2.COLOR_BGR2HSV)


  Lp,ap,bp = cv2.split(lab)

  # 土砂検出
  _landslide = (Lp>128)&(ap>128)

  idx = np.where(_landslide)
  bl[idx],gl[idx],rl[idx] = (bo[idx]*al+100*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+230*(1-al))
  _lnd[idx] = 0

  lnd = np.dstack((np.dstack((bl,gl)),rl))

  cv2.imwrite('results/mask/_landslide.png', _lnd)
  cv2.imwrite('results/landslide.png', lnd)

  return _lnd


def rejection(org,img):
  h,w,_ = img.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  bv,gv,rv = cv2.split(org)
  b,g,r = cv2.split(org)
  _veg = np.full((h,w), 255)
  _rej = np.full((h,w), 255)

  lab,hsv = cv2.cvtColor(img,cv2.COLOR_BGR2Lab),cv2.cvtColor(img,cv2.COLOR_BGR2HSV)



  Lp,ap,bp = cv2.split(lab)
  hp,sp,vp = cv2.split(hsv)

  # 植生
  _vegitation = ((ap<120)|(bp<120))&(hp>20)

  idx = np.where(_vegitation)

  bv[idx],gv[idx],rv[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  b[idx],g[idx],r[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  _veg[idx],_rej[idx] = 0,0

  veg = np.dstack((np.dstack((bv,gv)),rv))
  cv2.imwrite('results/mask/_vegitation.png', _veg)
  cv2.imwrite('results/vegitation.png', veg)

  return _veg
