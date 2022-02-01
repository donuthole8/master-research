import cv2
from cv2 import resizeWindow
from matplotlib import pyplot as plt
from osgeo import gdal,osr
import numpy as np



def write_tiffile(res,read_file,write_file):
  """
  tifファイルの保存
  """
  # Nodataの消去
  # idx = np.where((res == 0) or (res == 12623735.))
  # res[idx] = -1
  print(len(res))

  # tif画像テンプレ読み込み
  src = gdal.Open(read_file)

  # 画像サイズ・バンド数
  xsize = src.RasterXSize
  ysize = src.RasterYSize
  band = src.RasterCount

  # 第1-4バンド
  b3,b2,b1 = res,res,res
  b4 = src.GetRasterBand(4).ReadAsArray()

  # データタイプ番号（32-bit float）
  dtid = 6

  # 出力画像
  output = gdal.GetDriverByName('GTiff').Create(write_file, xsize, ysize, band, dtid)

  # 座標系指定
  output.SetGeoTransform(src.GetGeoTransform())

  # 空間情報を結合
  output.SetProjection(src.GetProjection())
  output.GetRasterBand(1).WriteArray(b1)
  output.GetRasterBand(2).WriteArray(b2)
  output.GetRasterBand(3).WriteArray(b3)
  output.GetRasterBand(4).WriteArray(b4)
  output.FlushCache()


def adjust_dsm(dsm_uav, dsm_heli):
  """
  解像度の調整・UAVのNoData部分を航空写真から切り取り
  """
  # 解像度を低い方のDSMに合わせる
  if (dsm_uav.shape[0] < dsm_heli.shape[0]):
    _dsm_uav = cv2.resize(dsm_uav, dsize=(dsm_uav.shape[1],dsm_uav.shape[0]))
    _dsm_heli = cv2.resize(dsm_heli, dsize=(dsm_uav.shape[1],dsm_uav.shape[0]))
  else:
    _dsm_uav = cv2.resize(dsm_uav, dsize=(dsm_heli.shape[1],dsm_heli.shape[0]))
    _dsm_heli = cv2.resize(dsm_heli, dsize=(dsm_heli.shape[1],dsm_heli.shape[0]))

  # UAVの解像度を下げる
  # _dsm_uav = cv2.resize(dsm_uav, dsize=(dsm_heli.shape[1],dsm_heli.shape[0]))

  # 航空写真DSMの不要範囲除去（UAVでの透過背景消去）
  idx = np.where(_dsm_uav == -32767.0)
  _dsm_heli[idx] = -32767.0

  # -300以下の値をNoDataにする
  idx = np.where(_dsm_uav < -300)
  _dsm_uav[idx],_dsm_heli[idx] = -999,-999

  return _dsm_uav,_dsm_heli


def resampling_dsm(dsm_uav, dsm_heli):
  """
  UAVのNoData部分を航空写真から切り取り・解像度のリサンプリング
  """
  # 共通一次内挿法により解像度が高い方のDSMに合わせる
  # UAVDSMと同じデータ大きさの配列作成
  _resize_dsm_heli,resize_dsm_heli = np.zeros(dsm_uav.shape),np.zeros(dsm_uav.shape)

  # 倍率を算出し倍率に応じてヘリ標高値を入れる
  magnification = dsm_uav.shape[1] / dsm_heli.shape[1]
  for i in range(dsm_uav.shape[0]):
    for j in range(dsm_uav.shape[1]):
      x = int(i/magnification)
      y = int(j/magnification)
      try:
        _resize_dsm_heli[i,j] = dsm_heli[x,y]
      except:
        _resize_dsm_heli[i,j] = dsm_heli[x-1,y-1]

  # 共通一次内挿法（3×3画素での加重平均）にてリサンプリング
  for i in range(1,dsm_uav.shape[0]-1):
    for j in range(1,dsm_uav.shape[1]-1):
      resize_dsm_heli[i,j] = (_resize_dsm_heli[i,j] * 0.25
        + (_resize_dsm_heli[i-1,j] + _resize_dsm_heli[i+1,j] + _resize_dsm_heli[i,j-1] + _resize_dsm_heli[i,j+1]) * 0.125
        + (_resize_dsm_heli[i-1,j-1] + _resize_dsm_heli[i-1,j+1] + _resize_dsm_heli[i+1,j-1] + _resize_dsm_heli[i+1,j+1]) * 0.625)

  # 航空写真DSMの不要範囲除去（UAVでの透過背景消去）
  idx = np.where(dsm_uav == -32767.0)
  resize_dsm_heli[idx] = -32767.0

  # -300以下の値をNoDataにする
  idx = np.where(dsm_uav < -300)
  dsm_uav[idx],resize_dsm_heli[idx] = -999,-999

  print(resize_dsm_heli.shape)

  write_tiffile(resize_dsm_heli, "test_uav.tif", "heli_resampling.tif")

  return dsm_uav,resize_dsm_heli


def _draw_histogram(dsm_uav,dsm_heli,name):
  # ヒストグラム比較
  plt.clf()
  # if (name=="_normalization"):
  #   hist_range=[-2,190]
  # else:
  #   hist_range=[-999999,147]
  plt.hist(dsm_uav.ravel(),bins=256,range=(-150,150),histtype="step",rwidth=0.5,color="teal",label="uav")
  plt.hist(dsm_heli.ravel(),bins=256,range=(-150,150),histtype="step",rwidth=0.5,color="darkred",label="gsi")
  plt.ylim(0,30000)
  plt.savefig(f"./histogram/uav&gsi{name}.png")

  cv2.imwrite("./results/dem_gsi_clipping.png",dsm_heli)


def draw_histogram(dsm_uav,dsm_heli,name):
  # ヒストグラム比較
  plt.clf()
  # if (name=="_normalization"):
  #   hist_range=[-2,190]
  # else:
  #   hist_range=[-999999,147]
  plt.hist(dsm_uav.ravel(),bins=256,range=(-30,185),histtype="step",rwidth=0.5,color="teal",label="uav")
  plt.hist(dsm_heli.ravel(),bins=256,range=(-30,185),histtype="step",rwidth=0.5,color="darkred",label="gsi")
  # plt.ylim(0,1800)
  plt.savefig(f"./histogram/uav&gsi{name}.png")

  cv2.imwrite("./results/dem_gsi_clipping.png",dsm_heli)


# def normalize_dsm(dsm,max_height):
#   # idx = np.where(dsm < -999)
#   # dsm[idx] = 255
#   # 最大・最小値算出（-32767はNo Dataであるため除く）
#   max_dsm,min_dsm = np.max(dsm),np.unique(dsm)[1]
#   # if (min_dsm < -999):
#   #   min_dsm = -130

#   # 標高値がヒストグラム上で重なるように手動設定
#   # min_uav = -36

#   # 標高最大値（山間部の頂上・植生頂上）の変化は無いと仮定する
#   # （標高最小値（海・海岸）は海抜0mと仮定する）
#   # UAVのDEMを0 - 180mに正規化

#   _dsm = (dsm-min_dsm)/(max_dsm-min_dsm) * max_height
#   # idx = np.where(_dsm == -21779.332)
#   # _dsm[idx] = -999
#   max_dsm,min_dsm = np.max(_dsm),np.min(_dsm)

#   # 正規化画像保存
#   cv2.imwrite("./results/normalization.png",_dsm)

#   return _dsm



def normalize_dsm(dsm_uav,dsm_heli,max_dsm_uav,min_dsm_uav):
  # 最大・最小値算出（-32767はNo Dataであるため除く）
  # max_dsm_uav,min_dsm_uav = np.max(dsm_uav),np.unique(dsm_uav)[1]
  # print(max_dsm_uav,min_dsm_uav)
  max_dsm_heli,min_dsm_heli = np.max(dsm_heli),np.unique(dsm_heli)[1]
  print(max_dsm_heli,min_dsm_heli)

  min_dsm_uav = -90
  # 標高最大値（山間部の頂上・植生頂上）の変化は無いと仮定する
  # （標高最小値（海・海岸）は海抜0mと仮定する）
  # UAVのDEMを0-180mに正規化
  # min_dsm_uav = 0
  # max_dsm_uav = 255


  # _dsm = (dsm-min_dsm)/(max_dsm-min_dsm) * max_height

  # 標高ちょっと考慮
  _dsm_uav = (dsm_uav-min_dsm_uav)/(max_dsm_uav-min_dsm_uav) * 185
  _dsm_heli = (dsm_heli-min_dsm_heli)/(max_dsm_heli-min_dsm_heli) * 190
  max_dsm_uav,min_dsm_uav = np.max(_dsm_uav),np.unique(_dsm_uav)[1]
  print(max_dsm_uav,min_dsm_uav)
  max_dsm_uav,min_dsm_uav = np.max(_dsm_heli),np.unique(_dsm_heli)[1]
  print(max_dsm_uav,min_dsm_uav)

  # # idx = np.where(_dsm == -21779.332)
  # # _dsm[idx] = -999
  # max_dsm,min_dsm = np.max(_dsm),np.min(_dsm)

  # 正規化画像保存
  # cv2.imwrite("./results/normalization.png",_dsm)

  return _dsm_uav,_dsm_heli

def calc_sedimentation(dsm_uav,dsm_heli):
  # 差分処理
  dsm_sub = dsm_uav - dsm_heli

  # UAVのDSMで0値は透過背景
  idx = np.where(dsm_uav == 12955939.0)
  dsm_sub[idx] = -999

  return dsm_sub


def calc_max_min(path):
  # 画像読み込み
  dsm_uav = cv2.imread(path,cv2.IMREAD_UNCHANGED)
  # 最大・最小値算出（-32767はNo Dataであるため除く）
  max_dsm_uav,min_dsm_uav = np.max(dsm_uav),np.unique(dsm_uav)[1]

  return max_dsm_uav,min_dsm_uav


# バイナリ書き出し
def write_binfile(data, path):
  """
  バイナリデータの書き出し
  """
  f = open(path, 'w')
  for i in data:
    for j in i:
      f.write(str(j) + ' ')
    f.write(str('\n'))
  f.close()


def check_data(dsm_uav,dsm_heli):
  """
  各入出力値を確認
  """
  # 最小値・最大値確認
  # max_dsm,min_dsm = np.max(dsm_uav),np.unique(dsm_uav)[1]
  # print(max_dsm,min_dsm)
  # max_dsm,min_dsm = np.max(dsm_heli),np.unique(dsm_heli)[1]
  # print(max_dsm,min_dsm)
  # サイズ・画素値確認
  # print(dsm_uav)
  # print(dsm_heli)
  print(dsm_uav.shape)
  print(dsm_heli.shape)
  # バイナリ書き出し・画素値確認
  # write_binfile(dsm_uav, './binary/dsm_uav.txt')
  # write_binfile(dsm_heli, './binary/dsm_heli.txt')
  # ヒストグラム描画
  _draw_histogram(dsm_uav,dsm_heli,"")

def sub_dim(dsm):
  # np.zeros(dsm_uav.shape)
  # _dsm = cv2.resize(dsm, dsize=(dsm.shape[1],dsm.shape[0]))
  _dsm = np.zeros((dsm.shape[0],dsm.shape[1]))

  for i in range(dsm.shape[0]):
    for j in range(dsm.shape[1]):
      _dsm[i,j] = dsm[i,j,0]

  return _dsm

# メイン関数
def main():
  # 入力画像読込
  # path1 = './images/dsm_uav_raw.tif'
  # path2 = './images/dsm_heli_clipping_raw.tif'
  path1 = 'test_uav.tif'
  path2 = 'test_heli.tif'
  dsm_uav = cv2.imread(path1, cv2.IMREAD_UNCHANGED)
  dsm_heli = cv2.imread(path2, cv2.IMREAD_UNCHANGED)


  # 4チャンネルを1チャンネルに変更
  _dsm_uav = sub_dim(dsm_uav)
  _dsm_heli = sub_dim(dsm_heli)

  print("uav : ", _dsm_uav.shape)
  print("heli : ", _dsm_heli.shape)

  # DMS切り抜き・解像度のリサンプリング
  dsm_uav,dsm_heli = resampling_dsm(_dsm_uav, _dsm_heli)

  # # 出力確認
  # check_data(dsm_uav,dsm_heli)

  # # 最小値・最大値算出
  # max_dsm,min_dsm = calc_max_min(path1)

  # # UAVのDSMの標高値調整
  # # _dsm_uav = normalize_dsm(dsm_uav,max_height)
  # # _dsm_heli = normalize_dsm(dsm_heli,max_height)
  # _dsm_uav,_dsm_heli = normalize_dsm(dsm_uav,dsm_heli,max_dsm,min_dsm)

  # # バイナリ書き出し・画素値確認
  # # write_binfile(normalized_dsm_uav, './binary/_dsm_uav.txt')
  # # print("wrote 1")
  # # write_binfile(normalized_dsm_heli, './binary/_dsm_heli.txt')
  # # print("wrote 2")

  # # ヒストグラム描画
  # draw_histogram(_dsm_uav,_dsm_heli,"_normalization")

  # # 堆積差分算出
  # dsm_sub = calc_sedimentation(_dsm_uav,_dsm_heli)

  # # バイナリ書き出し
  # # write_binfile(dsm_sub, './binary/dsm_sub.txt')

  # # 堆積差分の正規化
  # # _dsm_sub = normalize_dsm(dsm_sub,100)
  # write_binfile(dsm_sub, './binary/_dsm_sub.txt')
  # max_dsm,min_dsm = np.max(dsm_uav),np.min(dsm_uav)
  # print(max_dsm,min_dsm)

  # # tif画像への書き出し
  # # ここのパスを合わせないとうまく行かない，小さい画像に合わせる，img形式
  # # write_tiffile(dsm_sub, "./images/dsm_heli_clipping_img.tif")
  # write_tiffile(dsm_sub, "./images/dsm_uav_img.tif")
  # print(dsm_sub)



if __name__ == "__main__":
  main()
