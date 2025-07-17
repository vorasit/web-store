 โปรเจ็คนี้คือ เว็บไซต์ E-commerce (ร้านค้าออนไลน์) ที่สร้างด้วยเฟรมเวิร์ก Django ของภาษา Python ครับ

  มีฟังก์ชันการทำงานหลักๆ ดังนี้:

   * ระบบจัดการสินค้า: แสดงรายการสินค้า (product_list.html) และรายละเอียดของสินค้าแต่ละชิ้น (product_detail.html)
   * ระบบตะกร้าสินค้า: ผู้ใช้สามารถเพิ่มสินค้าลงในตะกร้า (cart.html)
   * ระบบสั่งซื้อและชำระเงิน: กระบวนการสั่งซื้อสินค้า (checkout.html), ยืนยันการสั่งซื้อ (order_confirmation.html) และดูประวัติการสั่งซื้อ
     (order_history.html)
   * ระบบสมาชิก: สมัครสมาชิก (register.html), เข้าสู่ระบบ (login.html), จัดการข้อมูลส่วนตัว (profile.html) และตั้งรหัสผ่านใหม่
   * ระบบรายการโปรด (Wishlist): บันทึกสินค้าที่สนใจไว้ดูภายหลัง (wishlist.html)
   * ระบบรีวิวสินค้า: ผู้ใช้สามารถให้คะแนนและเขียนรีวิวสินค้าได้ (จากไฟล์ migrations/0004_review.py)
   * ระบบคูปองส่วนลด: รองรับการใช้คูปองเพื่อเป็นส่วนลดในการสั่งซื้อ (จากไฟล์ migrations/0010_coupon_...)


จากไฟล์ store/models.py มีโครงสร้างข้อมูลของร้านค้าดังนี้ครับ:

   * `Category`: จัดหมวดหมู่สินค้า (เช่น เสื้อผ้า, อิเล็กทรอนิกส์)
   * `Product`: ข้อมูลสินค้าแต่ละชิ้น เช่น ชื่อ, รายละเอียด, ราคา, จำนวนคงคลัง (stock), และรูปภาพ โดยแต่ละสินค้าจะอยู่ใน Category ใด
     Category หนึ่ง
   * `Cart` และ `CartItem`: จัดการตะกร้าสินค้าของผู้ใช้ที่ยังไม่ได้ล็อกอิน (ใช้ cart_id ใน session) CartItem
     คือสินค้าแต่ละรายการที่อยู่ในตะกร้า
   * `Order` และ `OrderItem`: เก็บข้อมูลการสั่งซื้อ Order จะเก็บข้อมูลสรุป เช่น ผู้สั่งซื้อ, ยอดรวม, สถานะการสั่งซื้อ (เช่น กำลังรอ,
     จัดส่งแล้ว), วิธีชำระเงิน, และข้อมูลการติดตามพัสดุ ส่วน OrderItem คือสินค้าแต่ละรายการในคำสั่งซื้อนั้นๆ
   * `Coupon`: จัดการคูปองส่วนลด ซึ่งมีรหัส, วันหมดอายุ, และเปอร์เซ็นต์ส่วนลด
   * `Review`: เก็บรีวิวและคะแนน (1-5 ดาว) ที่ผู้ใช้มีต่อสินค้าแต่ละชิ้น
   * `Wishlist`: รายการสินค้าที่ผู้ใช้กด "ถูกใจ" หรือ "อยากได้" เก็บไว้ดูภายหลัง
   * `UserProfile`: เก็บข้อมูลเพิ่มเติมของผู้ใช้ที่ลงทะเบียนแล้ว เช่น ที่อยู่ (address) ซึ่งเชื่อมต่อกับโมเดล User หลักของ Django

      *Signals: โค้ดสองส่วนท้ายสุด (create_user_profile และ save_user_profile) เป็นการทำงานอัตโนมัติ เมื่อมี User
     ใหม่ถูกสร้างขึ้นในระบบ จะมีการสร้าง UserProfile ที่ผูกกันให้ทันที



จากไฟล์ store/urls.py เราจะเห็นการจับคู่ระหว่าง URL path กับฟังก์ชันที่อยู่ใน views.py (ซึ่งเป็นตัวจัดการ logic ของแต่ละหน้า)
  ได้ดังนี้ครับ:

  หน้าหลักและสินค้า:
   * '' (หน้าแรกสุด): แสดงรายการสินค้าทั้งหมด (views.product_list)
   * '<slug:category_slug>/': แสดงรายการสินค้าตามหมวดหมู่ (views.product_list)
   * '<slug:slug>/': แสดงรายละเอียดของสินค้าหนึ่งชิ้น (views.product_detail)


  ตะกร้าสินค้า (Cart):
   * 'cart/': แสดงหน้ารายละเอียดตะกร้าสินค้า (views.cart_detail)
   * 'add/<int:product_id>/': URL สำหรับเพิ่มสินค้าลงตะกร้า (views.add_cart)
   * 'remove/<int:product_id>/': URL สำหรับลดจำนวนสินค้าในตะกร้า (views.remove_cart)
   * 'full_remove/<int:product_id>/': URL สำหรับลบสินค้าออกจากตะกร้าทั้งหมด (views.remove_full_cart)


  การสั่งซื้อ (Order):
   * 'checkout/': หน้าสำหรับกรอกข้อมูลเพื่อสั่งซื้อ (views.checkout)
   * 'order_confirmation/<int:order_id>/': หน้ายืนยันการสั่งซื้อสำเร็จ (views.order_confirmation)
   * 'order_history/': หน้าประวัติการสั่งซื้อทั้งหมดของผู้ใช้ (views.order_history)
   * 'order_detail/<int:order_id>/': หน้ารายละเอียดของคำสั่งซื้อเฉพาะ (views.order_detail)


  ผู้ใช้และโปรไฟล์:
   * 'register/': หน้าสมัครสมาชิก (views.register)
   * 'profile/': หน้าโปรไฟล์ผู้ใช้ (views.profile)
   * 'profile/edit/': หน้าแก้ไขข้อมูลโปรไฟล์ (views.profile_edit)


  รายการโปรด (Wishlist):
   * 'wishlist/': หน้าแสดงรายการสินค้าที่อยากได้ (views.wishlist_view)
   * 'wishlist/add/<int:product_id>/': URL สำหรับเพิ่มสินค้าใน Wishlist (views.add_to_wishlist)
   * 'wishlist/remove/<int:product_id>/': URL สำหรับลบสินค้าออกจาก Wishlist (views.remove_from_wishlist)


  อื่นๆ:
   * 'coupon_apply/': URL สำหรับใช้คูปองส่วนลด (views.coupon_apply)
   * 'stripe-webhook/': URL สำหรับรับข้อมูลการชำระเงินจาก Stripe (Payment Gateway)
     ซึ่งหมายความว่าโปรเจคนี้มีการเชื่อมต่อกับระบบชำระเงินออนไลน์ Stripe ด้วย (views.stripe_webhook)
