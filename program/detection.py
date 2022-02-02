import cv2
import numpy as np

import preprocessing


def create_gamma_img(gamma, img):
  gamma_cvt = np.zeros((256,1), dtype=np.uint8)
  for i in range(256):
    gamma_cvt[i][0] = 255*(float(i)/255)**(1.0/gamma)
  return cv2.LUT(img, gamma_cvt)


def correction_whiteout(org, img):
  bo,go,ro = cv2.split(org)
  b,g,r = cv2.split(org)
  lab = cv2.cvtColor(img,cv2.COLOR_BGR2Lab)
  hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
  Lp,ap,bp = cv2.split(lab)

  al = 0.45

  # 白土砂検出
  _white = (Lp>240)

  idx = np.where(_white)
  b[idx],g[idx],r[idx] = (bo[idx]*al+200*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+100*(1-al))
  shadow = np.dstack((np.dstack((b,g)),r))

  # ガンマ補正，領域内だけできるといーね
  # img = create_gamma_img(0.5,img)
  # imgs = cv2.hconcat([img, gamma])

  # lab = cv2.cvtColor(img,cv2.COLOR_BGR2Lab)
  # Lp,ap,bp = cv2.split(lab)


  # 影領域の輝度補正
  # 入力画像の影だけ明るく
  # ll,aa,bb = cv2.split(cv2.cvtColor(org,cv2.COLOR_BGR2LAB))
  # ll[idx] -= 192
  # img = cv2.cvtColor(np.dstack((np.dstack((ll,aa)),bb)),cv2.COLOR_LAB2BGR)

  Lp[idx] -= 64
  img = cv2.cvtColor(np.dstack((np.dstack((Lp,ap)),bp)),cv2.COLOR_LAB2BGR)

  # vp[idx] = 150
  # corrected_shadow = cv2.cvtColor(np.dstack((np.dstack((hp,sp)),vp)),cv2.COLOR_HSV2BGR)

  # b[idx],g[idx],r[idx] = b[idx]*10,g[idx]*10,r[idx]*10
  # corrected_shadow = np.dstack((np.dstack((b,g)),r))

  cv2.imwrite('results/whiteout.png', shadow)
  cv2.imwrite('results/corrected_wh.png', img)

  return img


def correction_shadow(org, img):
  bo,go,ro = cv2.split(org)
  b,g,r = cv2.split(org)
  lab = cv2.cvtColor(img,cv2.COLOR_BGR2Lab)
  hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
  Lp,ap,bp = cv2.split(lab)
  hp,sp,vp = cv2.split(hsv)

  al = 0.45

  # 影検出
  _shadow = (Lp<10)

  idx = np.where(_shadow)
  b[idx],g[idx],r[idx] = (bo[idx]*al+200*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+100*(1-al))
  shadow = np.dstack((np.dstack((b,g)),r))

  # ガンマ補正，領域内だけできるといーね
  img = create_gamma_img(3,img)
  # imgs = cv2.hconcat([img, gamma])

  lab = cv2.cvtColor(img,cv2.COLOR_BGR2Lab)
  Lp,ap,bp = cv2.split(lab)


  # 影領域の輝度補正
  # 入力画像の影だけ明るく
  # ll,aa,bb = cv2.split(cv2.cvtColor(org,cv2.COLOR_BGR2LAB))
  # ll[idx] += 192
  # corrected_shadow = cv2.cvtColor(np.dstack((np.dstack((ll,aa)),bb)),cv2.COLOR_LAB2BGR)

  # # ミーンシフトとか
  # img = preprocessing.meanshift(corrected_shadow,10,10,300)
  # img = preprocessing.equalization(img)
  # img = preprocessing.quantization(img)


  Lp[idx] += 192
  img = cv2.cvtColor(np.dstack((np.dstack((Lp,ap)),bp)),cv2.COLOR_LAB2BGR)

  # vp[idx] = 150
  # corrected_shadow = cv2.cvtColor(np.dstack((np.dstack((hp,sp)),vp)),cv2.COLOR_HSV2BGR)


  # b[idx],g[idx],r[idx] = b[idx]*10,g[idx]*10,r[idx]*10
  # corrected_shadow = np.dstack((np.dstack((b,g)),r))

  cv2.imwrite('results/shadow.png', shadow)
  cv2.imwrite('results/corrected_shadow.png', img)

  return img


def detection(org,img):
  h,w,_ = img.shape
  bo,go,ro = cv2.split(org)
  al = 0.45

  bl,gl,rl = cv2.split(org)
  _lnd = np.full((h,w), 255)

  lab,hsv = cv2.cvtColor(img,cv2.COLOR_BGR2Lab),cv2.cvtColor(img,cv2.COLOR_BGR2HSV)


  Lp,ap,bp = cv2.split(lab)

  # 土砂検出
  _landslide = (Lp>100)&(ap>100)
  # _landslide = (Lp>100)&(ap>10)

  idx = np.where(_landslide)
  bl[idx],gl[idx],rl[idx] = (bo[idx]*al+100*(1-al)),(go[idx]*al+70*(1-al)),(ro[idx]*al+230*(1-al))
  _lnd[idx] = 0

  # mask = np.zeros((img.shape[0],img.shpae[1]))
  # mask[idx] = np.where(_landslide)

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
  # _vegitation = ((ap<120)|(bp<120))

  idx = np.where(_vegitation)

  bv[idx],gv[idx],rv[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  b[idx],g[idx],r[idx] = (bo[idx]*al+40*(1-al)),(go[idx]*al+220*(1-al)),(ro[idx]*al+140*(1-al))
  _veg[idx],_rej[idx] = 0,0

  veg = np.dstack((np.dstack((bv,gv)),rv))
  cv2.imwrite('results/mask/_vegitation.png', _veg)
  cv2.imwrite('results/vegitation.png', veg)

  return _veg
