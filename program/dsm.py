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


def resampling_dsm(dsm_uav, dsm_heli):
  """
  UAVのNoData部分を航空写真から切り取り・解像度のリサンプリング
  """
  # バイキュービック補間で解像度統一
  resize_dsm_heli = cv2.resize(dsm_heli, (dsm_uav.shape[1],dsm_uav.shape[0]), interpolation=cv2.INTER_CUBIC)

  # 航空写真DSMの不要範囲除去（UAVでの透過背景消去）
  idx = np.where(dsm_uav == -32767.0)
  resize_dsm_heli[idx] = -32767.0
  idx = np.where(dsm_uav < -100)
  dsm_uav[idx],resize_dsm_heli[idx] = None,None

  # dsm_uav[idx] = None
  # idx = np.where(dsm_heli < -100)
  # resize_dsm_heli[idx] = np.nan

  print("re uav-size : ",dsm_uav.shape)
  print("re heli-size :",resize_dsm_heli.shape)

  write_tiffile(resize_dsm_heli, './images/dsm_uav_img.tif', './results/heli_resampling.tif')

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


def draw_histogram(dsm_uav,dsm_heli):
  # ヒストグラム比較
  plt.clf()
  plt.hist(dsm_uav.ravel(),bins=256,range=(0,200),histtype="step",rwidth=0.5,color="teal",label="uav")
  plt.hist(dsm_heli.ravel(),bins=256,range=(0,200),histtype="step",rwidth=0.5,color="darkred",label="heli")
  plt.savefig(f"./histogram/uav&heli.png")


def remove_vegitation(dsm_uav,dsm_heli):
  # 植生領域マスク
  _veg = cv2.imread("./images/_vegitation.png")

  veg = cv2.split(_veg)[0]
  print("->veg",veg.shape)


  # マスク処理
  idx = np.where(veg < 128)
  dsm_uav[idx] = None
  dsm_heli[idx] = None

  return dsm_uav,dsm_heli


def detect_sedimentation(dsm):
  # 土砂領域マスク
  _sed = cv2.imread("./images/_landslide.png")

  sed = cv2.split(_sed)[0]
  print("->sed",sed.shape)


  # マスク処理
  idx = np.where(sed > 128)
  dsm[idx] = None

  return dsm


def normalize_dsm(dsm_uav,dsm_heli):
  # 最小値・最大値算出
  min_dsm_uav,max_dsm_uav = calc_min_max(dsm_uav)
  print("uav-range : ", min_dsm_uav, max_dsm_uav)
  min_dsm_heli,max_dsm_heli = calc_min_max(dsm_heli)
  print("heli-range : ", min_dsm_heli, max_dsm_heli)

  # 標高最大値（山間部の頂上・植生頂上）の変化は無いと仮定する
  # （標高最小値（海・海岸）は海抜0mと仮定する）
  # UAVのDEMを0-180mに正規化
  # 最大標高180m，最小標高0mとする
  max_height_uav = 190
  max_height_heli = 185

  # 正規化処理
  _dsm_uav = (dsm_uav-min_dsm_uav)/(max_dsm_uav-min_dsm_uav) * max_height_uav
  _dsm_heli = (dsm_heli-min_dsm_heli)/(max_dsm_heli-min_dsm_heli) * max_height_heli

  # # 外れ値除去
  # idx = np.where(_dsm_uav > 180)
  # _dsm_uav[idx] = 180
  # min_dsm_uav,max_dsm_uav = calc_min_max(_dsm_uav)
  # _dsm_uav = (_dsm_uav-min_dsm_uav)/(max_dsm_uav-min_dsm_uav) * 180



  # # 標高ちょっと考慮
  # _dsm_uav = (dsm_uav-min_dsm_uav)/(max_dsm_uav-min_dsm_uav) * 185
  # _dsm_heli = (dsm_heli-min_dsm_heli)/(max_dsm_heli-min_dsm_heli) * 190
  # max_dsm_uav,min_dsm_uav = np.max(_dsm_uav),np.unique(_dsm_uav)[1]
  # print(max_dsm_uav,min_dsm_uav)
  # max_dsm_uav,min_dsm_uav = np.max(_dsm_heli),np.unique(_dsm_heli)[1]
  # print(max_dsm_uav,min_dsm_uav)

  # # idx = np.where(_dsm == -21779.332)
  # # _dsm[idx] = -999
  # max_dsm,min_dsm = np.max(_dsm),np.min(_dsm)

  # 正規化画像保存
  # cv2.imwrite("./results/normalization.png",_dsm)

  return _dsm_uav,_dsm_heli


def standardization_dsm(dsm_uav,dsm_heli):
  # 平均・標準偏差算出
  ave_dsm_uav,sd_dsm_uav = calc_ave_sd(dsm_uav)
  print("uav-ave,sd : ", ave_dsm_uav, sd_dsm_uav)
  ave_dsm_heli,sd_dsm_heli = calc_ave_sd(dsm_heli)
  print("heli-ave,sd : ", ave_dsm_heli, sd_dsm_heli)

  # 標高最大値（山間部の頂上・植生頂上）の変化は無いと仮定する
  # （標高最小値（海・海岸）は海抜0mと仮定する）
  # UAVのDEMを0-180mに正規化
  # 最大標高180m，最小標高0mとする
  max_height_uav = 190
  max_height_heli = 185

  _dsm_uav = (dsm_uav-ave_dsm_uav)/sd_dsm_uav * max_height_uav
  _dsm_heli = (dsm_heli-ave_dsm_heli)/sd_dsm_heli * max_height_heli

  return _dsm_uav,_dsm_heli


def calc_sedimentation(dsm_uav,dsm_heli):
  # 標高差分を算出
  dsm_sub = dsm_uav - dsm_heli

  return dsm_sub


def calc_min_max(dsm):
  # 最大値と最小値を算出
  _min,_max = np.nanmin(dsm),np.nanmax(dsm)

  return _min, _max


def calc_ave_sd(dsm):
  # 平均と標準偏差を算出
  ave,sd = np.nanmean(dsm),np.nanstd(dsm)

  return ave,sd


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


# メイン関数
def main():
  # 入力画像読込
  path1 = './images/dsm_uav_raw.tif'
  path2 = './images/dsm_heli_clipping_raw.tif'
  # path2 = './images/dem_gsi_clipping.tif'
  dsm_uav = cv2.imread(path1, cv2.IMREAD_UNCHANGED)
  dsm_heli = cv2.imread(path2, cv2.IMREAD_UNCHANGED)

  print("uav-size : ", dsm_uav.shape)
  print("heli-size : ", dsm_heli.shape)

  # DMS切り抜き・解像度のリサンプリング
  dsm_uav,dsm_heli = resampling_dsm(dsm_uav, dsm_heli)

  # 植生領域除去
  dsm_uav,dsm_heli = remove_vegitation(dsm_uav,dsm_heli)

  # UAVのDSMの標高値調整
  _dsm_uav,_dsm_heli = normalize_dsm(dsm_uav,dsm_heli)
  # _dsm_uav,_dsm_heli = standardization_dsm(dsm_uav,dsm_heli)

  # ヒストグラム描画
  draw_histogram(_dsm_uav,_dsm_heli)

  # 堆積差分算出
  dsm_sub = calc_sedimentation(_dsm_uav,_dsm_heli)

  # 土砂領域のみを算出
  dsm_sub = detect_sedimentation(dsm_sub)

  # tif画像への書き出し
  write_tiffile(dsm_sub, "./images/dsm_uav_img.tif", "./results/dsm_sub_res.tif")


if __name__ == "__main__":
  main()
