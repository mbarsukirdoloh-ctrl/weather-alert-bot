import os
import requests

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
LATITUDE = os.environ.get("LATITUDE")
LONGITUDE = os.environ.get("LONGITUDE")
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

def send_line_notify(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    print("LINE API Response:", response.status_code, response.text)
    return response.status_code

def check_forecast_weather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}&units=metric&lang=th"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            city_name = data["city"]["name"]
            forecast_list = data["list"][:3]
            rain_alert_triggered = False
            alert_messages = []
            for item in forecast_list:
                dt_txt = item["dt_txt"]
                weather_desc = item["weather"][0]["description"]
                pop = item.get("pop", 0) * 100
                temp = item["main"]["temp"]
                if item["weather"][0]["main"].lower() in ["rain", "thunderstorm"] or pop >= 50:
                    rain_alert_triggered = True
                    alert_messages.append(f"⏰ เวลา {dt_txt}\n🌧️ {weather_desc} (โอกาสฝนตก {pop:.0f}%)\n🌡️ อุณหภูมิ: {temp}°C")
            
            # ทดสอบส่งข้อความแจ้งเตือนหรือดึง User ID
            if rain_alert_triggered:
                msg = f"⚠️ แจ้งเตือนพยากรณ์ฝนล่วงหน้า!\n📍 พื้นที่: {city_name}\n\n" + "\n\n".join(alert_messages)
                send_line_notify(msg)
            else:
                # ส่งข้อความสถานะปกติไปก่อนเพื่อให้แน่ใจว่าบอทส่งหาเราได้สำเร็จ
                send_line_notify(f"🤖 บอทรายงานตัวครับ: พื้นที่ {city_name} ช่วงนี้ไม่มีพยากรณ์ฝนตกใน 9 ชม. นี้ แต่ระบบทำงานปกติครับ!")
                print("ส่งข้อความสถานะปกติเข้า LINE เรียบร้อยแล้ว")
        else:
            print("ไม่สามารถดึงข้อมูลได้:", data.get("message"))
    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)

if __name__ == "__main__":
    check_forecast_weather()
