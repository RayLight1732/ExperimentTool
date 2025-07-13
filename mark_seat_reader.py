import cv2
from cv2 import aruco
import numpy as np
import dataclasses
from typing import Tuple,Optional,Union,List


class CorrectionProcessor:
    def __init__(
        self,
        width: int,
        height: int,
        preset_ids=[0, 1, 3, 2],
        preset_corner_ids=[2, 3, 0, 1],
    ):
        self.dic_aruco = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

        # マーカー四角形の指定
        self.preset_ids = preset_ids  # 現実世界で貼るマーカーのid(左上から時計回り)
        self.preset_corner_ids = (
            preset_corner_ids  # 各マーカーのどの頂点の座標を取得するか
        )
        self.rectW = width
        self.rectH = height
        self.pts2 = np.float32(
            [(0, 0), (self.rectW, 0), (self.rectW, self.rectH), (0, self.rectH)]
        )  # 長方形座標

    def get_rectangle(self, frame):
        """
        対応する四角形の頂点を左上から時計回りで返す
        見つからなかった場合、Noneを返す
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # グレースケールにする
     
        corners, ids, _ = aruco.detectMarkers(
            gray, self.dic_aruco
        )  # マーカー検出 corners(N,1,4,2) ids(N,1)

        list_ids = np.ravel(ids)  # idsを一次元化する
        pt = {}
        for id, corner in zip(list_ids, corners):  # まずは検出結果について
            pt[id] = corner[0]  # idとcornerを紐づける
        pts = []
        for id, corner_id in zip(self.preset_ids, self.preset_corner_ids):
            corner = pt.get(id)
            if corner is not None:
                pts.append(corner[corner_id])  # 特定の頂点の座標を順にリストに追加する
        pts1 = np.float32(pts)  # 投影変換する前の四角形
        print(f"found:{list_ids}")
        if len(pts1) == 4:  # 頂点が4つ見つかったとき
            return pts1
        else:
            return None

    def correct(self, frame)->Union[Tuple[cv2.typing.MatLike,np.ndarray],Tuple[None,None]]:
        pts1 = self.get_rectangle(frame)
        if pts1 is not None:
            M = cv2.getPerspectiveTransform(pts1, self.pts2)  # 投影行列
            rect = cv2.warpPerspective(
                frame, M, (self.rectW, self.rectH)
            )  # 長方形画像を得る
            return rect,pts1
        else:
            return None,None
            
    def overlay_mask(
        self,
        base_img: np.ndarray,
        mask_img:Union[cv2.typing.MatLike,List[cv2.typing.MatLike]],
        pts1: np.ndarray,
        alpha: float = 1.0,
        color: tuple[int, int, int] = (0, 0, 0),
    ) -> np.ndarray:
        """
        get_rectangle() で得た領域に、マスク画像を射影変換して指定色で重ねる。

        :param base_img: 元画像（カラー）
        :param mask_imgs: マスク画像(0=マーク部分)
        :param pts1: 実画像上の投影先四角形 (上から時計回りの4点)
        :param alpha: 色の不透明度 (1.0で完全塗りつぶし）
        :param color: 上書きする色 (B, G, R) タプル
        :return: 合成済み画像
        """
        mask_imgs = mask_img if isinstance(mask_img,list) else [mask_img]
        cv2.imshow("window0",cv2.resize(mask_imgs[0],(0,0),fx=0.5,fy=0.5))
        # マスク画像（rect → 台形）へ投影変換
        resized_mask_imgs = [cv2.resize(mask_img,(self.rectW,self.rectH)) for mask_img in mask_imgs]
        M = cv2.getPerspectiveTransform(self.pts2, pts1)
        warped_mask = [cv2.warpPerspective(resized_mask_img, M, (base_img.shape[1], base_img.shape[0]),borderValue=1) for resized_mask_img in resized_mask_imgs]
        warped_mask_array = np.stack(warped_mask)
        combined_mask = np.any(warped_mask_array, axis=0)
        cv2.imshow("window",cv2.resize(combined_mask.astype(np.uint8)*255,(0,0),fx=0.5,fy=0.5))
        # 重ねる対象領域（マスクが白の部分）
        mask_area = combined_mask == 1

        result_img = base_img.copy()
        # 対象ピクセルだけ色を変更
        if alpha >= 1.0:
            result_img[mask_area] = color
        else:
            result_img[mask_area] = (
                result_img[mask_area].astype(np.float32) * (1 - alpha)
                + np.array(color, dtype=np.float32) * alpha
            ).astype(np.uint8)

        return result_img
    
@dataclasses.dataclass(frozen=True)
class Margin:
    """各マークの上下左右にある余白を表すデータクラス"""

    margin_top: int = 0
    margin_left: int = 0
    margin_right: int = 0
    margin_bottom: int = 0


class MarkseatReader:
    """
    マークシート画像を読み取り、マークされた列インデックスを検出・可視化するクラス
    """

    def __init__(
        self,
        rect_margin: Margin,
        row: int,
        col: int,
        cell_width: int,
        cell_height: int,
        cell_margin: Margin,
    ):
        self.offset_top = rect_margin.margin_top
        self.offset_left = rect_margin.margin_left
        self.offset_bottom = rect_margin.margin_bottom
        self.offset_right = rect_margin.margin_right

        self.row = row
        self.col = col
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.cell_margin = cell_margin

    def read(self, src: np.ndarray) -> list[list[int]]:
        """
        マークシートを読み取り、各行のマークされた列インデックスのリストを返す
        """
        resized = self._resize(src)
        region = self._extract_region(resized)
        binary = self._binarize_image(region)
        return [self._analyze_row(binary, r) for r in range(self.row)]

    def create_mask(self,marked: list[list[int]]):
        cell_width, cell_height = self._calculate_cell_size()
        width = self.offset_left + self.col * cell_width + self.offset_right
        height = self.offset_top + self.row * cell_height + self.offset_bottom
        mask = np.zeros((height,width), dtype=np.uint8)   # 黒背景
        drawn = self._draw_cells(mask, marked, thickness=-1,color=1)
        return drawn

    def highlight_all_cells(self, src: np.ndarray) -> np.ndarray:
        """
        全セルの領域に枠線を描画してマーク位置を可視化する（確認用）

        :param src: 入力画像（グレースケール）
        :return: 枠線付き画像
        """
        marked = [[i for i in range(self.col)] for _ in range(self.row)]
        return self._draw_cells(src, marked, thickness=2,color=1)

    def fill_marked_cells(self, src: np.ndarray, marked: list[list[int]]) -> np.ndarray:
        """
        マークされたセルを塗りつぶして可視化する

        :param src: 入力画像（グレースケール）
        :param marked: 各行のマークされた列インデックス
        :return: 塗りつぶし描画済み画像
        """
        return self._draw_cells(src, marked, thickness=-1)

    def _draw_cells(
        self, src: np.ndarray, marked: list[list[int]], thickness: int,color=0
    ) -> np.ndarray:
        """
        指定されたセルに矩形を描画する共通処理

        :param src: 入力画像
        :param marked: 各行の対象セルインデックスリスト
        :param thickness: 線幅（-1なら塗りつぶし)
        :return: 描画済み画像
        """
        resized = self._resize(src)
        for row_index, col_indices in enumerate(marked):
            for col_index in col_indices:
                top_left = self._get_cell_position(row_index, col_index)
                bottom_right = (top_left[0] + self.cell_width, top_left[1] + self.cell_height)
                cv2.rectangle(
                    resized, top_left, bottom_right, color=color, thickness=thickness
                )

        return cv2.resize(resized, src.shape[::-1])

    def _resize(self, src: np.ndarray) -> np.ndarray:
        """
        マーク領域が正確に収まるサイズに画像をリサイズする
        """
        cell_width, cell_height = self._calculate_cell_size()
        width = self.offset_left + self.col * cell_width + self.offset_right
        height = self.offset_top + self.row * cell_height + self.offset_bottom
        return cv2.resize(src, (width, height))

    def _extract_region(self, src: np.ndarray) -> np.ndarray:
        """
        マーク部分だけを画像から切り出す
        """
        cell_width, cell_height = self._calculate_cell_size()
        x0 = self.offset_left
        y0 = self.offset_top
        x1 = x0 + self.col * cell_width
        y1 = y0 + self.row * cell_height
        return src[y0:y1, x0:x1]

    def _binarize_image(self, src: np.ndarray) -> np.ndarray:
        """
        各セルを個別に二値化し、その他の領域は黒で埋めた画像を返す

        :param src: 切り出されたマーク領域画像（グレースケール）
        :return: セル部分のみを反転二値化した画像（それ以外は黒）
        """
        output = np.zeros_like(src)  # 全体を黒（0）で初期化

        for row_index in range(self.row):
            for col_index in range(self.col):
                x, y = self._get_cell_position_in_rect(row_index, col_index)
                cell = src[y : y + self.cell_height, x : x + self.cell_width]
                # TODO ガウスノイズかけてもいいかも
                # セルごとにOtsuでしきい値処理（マーク＝白、背景＝黒）
                _, cell_bin = cv2.threshold(
                    cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )

                # 出力画像に埋め込む
                output[y : y + self.cell_height, x : x + self.cell_width] = cell_bin

        return output

    def _analyze_row(self, binary: np.ndarray, row_index: int) -> list[int]:
        """
        1行分の各セルを平均輝度で分析し、マークされている列を返す
        """
        means = []
        for col_index in range(self.col):
            x, y = self._get_cell_position_in_rect(row_index, col_index)
            cell = binary[y : y + self.cell_height, x : x + self.cell_width]
            mean = cv2.mean(cell)[0]
            means.append(mean)

        threshold = sum(means) / len(means)
        return [i for i, val in enumerate(means) if self._is_marked(val, threshold)]

    def _is_marked(self, value: float, threshold: float) -> bool:
        """
        平均輝度が閾値の1.4倍より高ければマークされたとみなす

        TODO 複数回答の場合、良くない
        二値化しているし、絶対値でいってもよさげ
        """
        return value > threshold * 1.4

    def _calculate_cell_size(self) -> tuple[int, int]:
        """
        セルサイズ（余白込み）を返す
        """
        cell_width = (
            self.cell_margin.margin_left + self.cell_width + self.cell_margin.margin_right
        )
        cell_height = (
            self.cell_margin.margin_top + self.cell_height + self.cell_margin.margin_bottom
        )
        return cell_width, cell_height

    def _get_cell_position(self, row: int, col: int) -> tuple[int, int]:
        """
        指定したセルの左上座標を返す（リサイズ済み画像内）
        """
        x_in_rect, y_in_rect = self._get_cell_position_in_rect(row, col)
        x = self.offset_left + x_in_rect
        y = self.offset_top + y_in_rect
        return x, y

    def _get_cell_position_in_rect(self, row: int, col: int) -> tuple[int, int]:
        """
        指定したセルの左上座標を返す（切り抜き済み画像内）
        """
        cell_width, cell_height = self._calculate_cell_size()
        x = col * cell_width + self.cell_margin.margin_left
        y = row * cell_height + self.cell_margin.margin_top
        return x, y


def main():
    # 1160 245
    # 280 100
    # 80 20
    processor = CorrectionProcessor(1000, 900)
    img = cv2.imread("c:\\Users\\arusu\\Downloads\\DSC_1158.jpg")
    corrected,rect = processor.correct(img)
    gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
    rect_margin = Margin(230, 1110, 0, 10)
    margin = Margin(15, 75, 75, 15)
    reader = MarkseatReader(
        rect_margin=rect_margin,
        row=16,
        col=4,
        cell_width=120,
        cell_height=60,
        cell_margin=margin,
    )

    result = reader.read(gray)
    for r in result:
        print(r)

    mask = reader.create_mask(result)
    draw = processor.overlay_mask(img,mask,rect,0.5)
    cv2.imshow("result", cv2.resize(draw,(400,500)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
