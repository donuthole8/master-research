import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import deque


def approximation(pix1, pix2):
  # L*a*b*表色系でdifを計算したほうがよさげ
  dif = abs(pix1 - pix2)
  dv = 15
  return (dif < dv).all()

def neighbours(idx, lim):
  w, h, _ = lim
  i, j = idx
  return sorted([
    (i + n, j + m)
    for n in range(-1, 2)
    for m in range(-1, 2)
    if not (n == 0 and m == 0) and i + n >= 0 and j + m >= 0 and i + n < w and j + m < h
  ])

def relabeling(dummy, src, idx, labels, label):
  q = deque([idx])
  while len(q) > 0:
    idx = q.popleft()
    labels[idx] = (label * 5, label * 10, label * 30)
    dummy[idx] = label
    ns = neighbours(idx, src.shape)
    q.extendleft(n for n in ns if approximation(src[n], src[idx]) and dummy[n] == 0)

def labeling(img,qua):
  h,w,c = img.shape
  # lab = cv2.cvtColor(img,cv2.COLOR_BGR2LAB)

  dummy = np.zeros((h, w), dtype=int)
  labels = np.zeros((h, w, c), dtype=int)
  label = 1

  it = np.nditer(img, flags=['multi_index'], op_axes=[[0, 1]])
  for n in it:
    if dummy[it.multi_index] == 0:
      relabeling(dummy, qua, it.multi_index,labels, label)
      # relabeling(dummy, lab, it.multi_index,labels, label)
      label += 1

  print('label number :',label)

  np.savetxt('results/dummy.txt',dummy.astype(np.uint8),fmt='%d')
  with open('results/label.txt', 'w') as f:
    print(label, file=f)
  cv2.imwrite('results/labeling.png', labels.astype(np.uint8))
  cv2.imwrite('results/dummy.png', dummy.astype(np.uint8))


def shortcut2():
  dummy = np.loadtxt('results/dummy.txt').astype(np.uint16)
  label = np.loadtxt('results/label.txt').astype(np.uint16)

def texture(img):
  mpl.rc('image', cmap='jet')
  pass
  kernel_size = 5
  levels = 8
  symmetric = False
  normed = True
  dst = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
  # binarize
  dst_bin = dst//(256//levels) # [0:255]->[0:7]

  # calc_glcm             
  h,w = dst.shape
  glcm = np.zeros((h,w,levels,levels), dtype=np.uint8)
  kernel = np.ones((kernel_size, kernel_size), np.uint8)
  dst_bin_r = np.append(dst_bin[:,1:], dst_bin[:,-1:], axis=1)
  for i in range(levels):
    for j in range(levels):
      mask = (dst_bin==i) & (dst_bin_r==j)
      mask = mask.astype(np.uint8)
      glcm[:,:,i,j] = cv2.filter2D(mask, -1, kernel)
  glcm = glcm.astype(np.float32)
  if symmetric:
    glcm += glcm[:,:,::-1, ::-1]
  if normed:
    glcm = glcm/glcm.sum(axis=(2,3), keepdims=True)
  # martrix axis
  axis = np.arange(levels, dtype=np.float32)+1
  w = axis.reshape(1,1,-1,1)
  x = np.repeat(axis.reshape(1,-1), levels, axis=0)
  y = np.repeat(axis.reshape(-1,1), levels, axis=1)
  # GLCM contrast
  glcm_contrast = np.sum(glcm*(x-y)**2, axis=(2,3))
  # GLCM dissimilarity
  glcm_dissimilarity = np.sum(glcm*np.abs(x-y), axis=(2,3))
  # GLCM homogeneity
  glcm_homogeneity = np.sum(glcm/(1.0+(x-y)**2), axis=(2,3))
  # GLCM energy & ASM
  glcm_asm = np.sum(glcm**2, axis=(2,3))
  # GLCM entropy
  ks = 5 # kernel_size
  pnorm = glcm / np.sum(glcm, axis=(2,3), keepdims=True) + 1./ks**2
  glcm_entropy = np.sum(-pnorm * np.log(pnorm), axis=(2,3))
  # GLCM mean
  glcm_mean = np.mean(glcm*w, axis=(2,3))
  # GLCM std
  glcm_std = np.std(glcm*w, axis=(2,3))
  # GLCM energy
  glcm_energy = np.sqrt(glcm_asm)
  # GLCM max
  glcm_max = np.max(glcm, axis=(2,3))
  
  # plot
  # plt.figure(figsize=(10,4.5))

  outs =[dst, glcm_mean, glcm_std,
    glcm_contrast, glcm_dissimilarity, glcm_homogeneity,
    glcm_asm, glcm_energy, glcm_max,
    glcm_entropy]
  titles = ['original','mean','std','contrast','dissimilarity','homogeneity','ASM','energy','max','entropy']
  for i in range(10):
    plt.imsave('results/tex/' + titles[i] + '.png', outs[i])
  
  return

def edge(img):
  dst = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

  canny = cv2.Canny(dst,100,450,5)
  sobelx = cv2.Sobel(dst,cv2.CV_64F,1,0,ksize=3)
  sobely = cv2.Sobel(dst,cv2.CV_64F,0,1,ksize=3)
  sobel = np.sqrt(sobelx**2 + sobely**2)
  laplacian = cv2.Laplacian(dst,cv2.CV_64F)
  
  cv2.imwrite('results/edge/canny.png', canny)
  cv2.imwrite('results/edge/sobelx.png', sobelx)
  cv2.imwrite('results/edge/sobely.png', sobely)
  cv2.imwrite('results/edge/sobel.png', sobel)
  cv2.imwrite('results/edge/laplacian.png', laplacian)

  return