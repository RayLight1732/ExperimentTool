from mark_seat_reader import MarkseatReader,Margin,CorrectionProcessor
import cv2

if __name__ == "__main__":
    rect_margin = Margin(285, 1110, 0, 60)
    margin = Margin(15, 75, 75, 15)
    markseat_reader = MarkseatReader(
        rect_margin=rect_margin,
        row=16,
        col=4,
        cell_width=120,
        cell_height=60,
        cell_margin=margin,
    )
    correction_processor = CorrectionProcessor(1000, 900)
    image = cv2.imread("c:\\Users\\arusu\\Downloads\\DSC_1164.jpg")
    corrected,rect = correction_processor.correct(image)
    if corrected is not None:
        #cv2.imshow("corrected",corrected)
        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
        highlight = markseat_reader.highlight_all_cells(gray)
        cv2.imshow("highlighted1",cv2.resize(highlight,(0,0),fx=0.5,fy=0.5))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("cannot find")