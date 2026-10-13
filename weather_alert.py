import os
import requests

# ดึงค่าพารามิเตอร์ความปลอดภัยจาก GitHub Secrets
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
LATITUDE = os.environ.get("LATITUDE")
LONGITUDE = os.environ.get("LONGITUDE")
LINE_TOKEN = os.environ.get("LINE_TOKEN")

def send_line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    return response.status_code

def check_forecast_weather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}&units=metric&lang=th"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            city_name = data["city"]["name"]
            forecast_list = data["list"][:3] # ตรวจสอบ 3 ช่วงเวลาถัดไป (รวม 9 ชั่วโมงข้างหน้า)
            
            rain_alert_triggered = False
            alert_messages = []
            
            for item in forecast_list:
                dt_txt = item["dt_txt"]
                weather_condition = item["weather"][0]["main"]
                weather_desc = item["weather"][0]["description"]
                pop = item.get("pop", 0) * 100
                temp = item["main"]["temp"]
                
                if weather_condition.lower() in ["rain", "thunderstorm"] or pop >= 50:
                    rain_alert_triggered = True
                    alert_messages.append(f"⏰ เวลา {dt_txt}\n🌧️ {weather_desc} (โอกาสฝนตก {pop:.0f}%)\n🌡️ อุณหภูมิ: {temp}°C")
            
            if rain_alert_triggered:
                msg = f"⚠️ แจ้งเตือนพยากรณ์ฝนล่วงหน้า!\n📍 พื้นที่: {city_name}\n\n" + "\n\n".join(alert_messages)
                send_line_notify(msg)
                print("ส่งข้อความแจ้งเตือนเข้า LINE เรียบร้อยแล้ว")
            else:
                print("ช่วงนี้ไม่มีพยากรณ์ฝนตกในระยะ 9 ชั่วโมงข้างหน้า")
        else:
            print("ไม่สามารถดึงข้อมูลพยากรณ์อากาศได้:", data.get("message"))
            
    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)

if __name__ == "__main__":
    check_forecast_weather()
