Cách bổ sung code vào các file


**hệ thống dùng selenium 4.10.0 nên sẽ không cần path của chromedriver nữa, mọi người update selenium nếu cần, sửa đoạn khởi tạo driver trong code sử dụng selenium của mình**

* File Crawl/base/URL.py :
    - bổ sung các link vào dict với vai trò tương ứng (nếu ko có thì để trống), trong link, sửa các giá trị dùng để replace khi tạo link (ví dụ SYMBOL, STARTDATE, ENĐATE, trong đó lần lượt là mã công ty, ngày bắt đầu lấy dữ liệu, ngày cuối cùng lấy dữ liệu)
    - Các hằng số phụ khác để như PATH_SAVE (nếu có)



* File Crawl/base/setup.py :
    - lưu các chức năng có thể sử dụng khi lấy dữ liệu ở các nguồn khác nhau. Các function trong này có khả năng sử dụng ở nhiều tình huống chứ không phải 1 tình huống cụ thể trên 1 nguồn dữ liệu. Có thể là function để check_list, save, ...


* Các file trong thư mục Crawl nhưng ngoài thư mục base:
    - Mỗi file xử lí cho 1 nguồn dữ liệu
    - Tạo một class (lấy tên là nguồn dữ liệu) và chuyển đổi các chức năng hiện tại (crawl, filter, getListCompany, ...) thành các method của class

* Comment chức năng mỗi hàm trong chương trình của mình, ví dụ như sau:
        def saveDataFrameCSV(self, dataframe, file_name):
            '''
            save dataframe to csv file
            '''
            try:
                dataframe.to_csv(f"{self.path_save}/{file_name}.csv", index= False)
            except:
                # raise Exception("Can't save file")
                print("Can't save file")
                pass

    thì "save dataframe to csv file" là mô tả về hàm 