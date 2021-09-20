import numpy as np
from osgeo import gdal, gdalconst, gdal_array
from osgeo import osr # 空間参照モジュール

src = gdal.Open('./images/_koyaura.tif', gdalconst.GA_ReadOnly) # tifの読み込み (read only)

xsize = src.RasterXSize
ysize = src.RasterYSize
band = src.RasterCount

# 第1-4バンド
b1 = src.GetRasterBand(1).ReadAsArray()
b2 = src.GetRasterBand(2).ReadAsArray()
b3 = src.GetRasterBand(3).ReadAsArray()
b4 = src.GetRasterBand(4).ReadAsArray()

# データタイプ番号
dtid = src.GetRasterBand(1).DataType
 # 型番号 -> 型名 変換
# print(gdal_array.GDALTypeCodeToNumericTypeCode(dtid))

# 座標に関する６つの数字 (下記参照)
print(src.GetGeoTransform())
# (132.51039360406432, 8.069859999998093e-07, 0.0, 34.30547758032056, 0.0, -6.696849999998514e-07)

# 座標系情報
print(src.GetProjection())
# GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]


# 出力画像
output = gdal.GetDriverByName('GTiff').Create('geo.tif', xsize, ysize, band, dtid)

# 座標系指定
output.SetGeoTransform(src.GetGeoTransform())

# 空間参照情報
srs = osr.SpatialReference()

# ここ火炎と間とがするぅ
srs.ImportFromEPSG(32648) # WGS84 UTM_48nに座標系を指定
output.SetProjection(srs.ExportToWkt()) # 空間情報を結合

output.GetRasterBand(1).WriteArray(b1)
output.GetRasterBand(2).WriteArray(b2)
output.GetRasterBand(3).WriteArray(b3)
output.GetRasterBand(4).WriteArray(b4)
output.FlushCache()
output = None
