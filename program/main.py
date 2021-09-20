import cv2
import prepro
import analysis
import detection
import postpro
import os


# 入力画像読込
#   - 地理情報を失わないのであればpng形式画像を用いるのが好ましい

path = 'images/_koyaura.tif'

prepro.read_tifffile(path)

if not os.path.isfile(path):
    raise FileNotFoundError('Image file not found!')
img = cv2.imread(path, cv2.IMREAD_COLOR)
print(int(img.shape[0]), ' x ', int(img.shape[1]), 'pix')

# 地理情報保存


# # サイズ縮小
# per = 1.0
# height = img.shape[0]
# width = img.shape[1]
# print(int(height*per),' x ',int(width*per),'pix')
# img = cv2.resize(img , (int(width*per), int(height*per)))

# デバッグモード
# import pdb; pdb.set_trace()

# オリジナル画像保存
org = img.copy()
cv2.imwrite('results/original.png', org)

# PyMeanShift
#   - Lab変換後の画像に適用
#   - 第１引数：探索範囲、第２引数：探索色相、第３引数：粗さ
# img = prepro.meanshift(img,10,10,300)
img = cv2.imread('./images/_meanshift.png', cv2.IMREAD_COLOR)

# ヒストグラム均一化
#   - Lab変換して処理した方が好ましい
#   - 明度以外のチャンネルも均一化した方が好ましい
img = prepro.equalization(img)

# 量子化・減色処理・ノイズ除去
#   - 領域分割後に類似領域に異色画素が散在してるため行う
img = prepro.quantization(img)

# img = cv2.medianBlur(img, 5)
# cv2.imwrite('results/median.png', img)

# img = cv2.bilateralFilter(img, 9, 75, 75)
# cv2.imwrite('results/bilateral.png', img)

# 類似色統合
img = prepro.clustering(img)

# 着目色（64色に減色）ごとに二値化（着目色とそれ以外、白黒ラベリングする）、そいで次の色に写って、、、、繰り返し
# 白黒ラベリング
# analysis.labeling(img,qua)

# カラーラベリング実行時間短縮
# analysis.shortcut2()

# テクスチャ解析
#   - img か org のどちらに適用するか関数内で選択
# methods.texture(img)
# methods.texture(org)

# エッジ抽出
#   - img か org のどちらに適用するか関数内で選択
# analysis.edge(img)
# analysis.edge(org)

# 災害領域検出
#   - 斜面崩壊・瓦礫でピクセル穴がある　
#   - 浸水検出結果で緑色のノイズがある
lnd, fld = detection.detection(org, img)

# 不要領域検出
# mask = methods.rejection()
mask, sky, veg, rbl, bld = detection.rejection(org, img)

# 最終出力
#   - tif形式でも出力したい
# _lnd,_fld = postpro.integration(mask,lnd,fld,sky,veg,rbl,bld,org)

# 精度評価
#   - 領域単位で評価
#   - 国土地理院の斜面崩壊判読図と比較
#   - 本手法ではピクセルベースでの精度評価
# postpro.evaluation(_lnd,_fld)
