import os
import discord
from discord.ext import commands
import requests
import re

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- ตั้งค่าเบอร์โทรศัพท์ของคุณ ---
MY_PHONE_NUMBER = "0936970343" 

# --- ใส่ ID ยศ VIP 99 เรียบร้อยแล้ว ---
TARGET_ROLE_ID = 154528904291077335  

class AngpaoModal(discord.ui.Modal, title='เติมเงินซื้อยศ (99 บาท)'):
    link = discord.ui.TextInput(
        label='กรอกลิงก์ซอง TrueMoney (99 บ.)',
        placeholder='https://gift.truemoney.com/campaign/?v=...',
        style=discord.TextStyle.short,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_link = self.link.value
        match = re.search(r'v=([a-zA-Z0-9]+)', user_link)
        
        if not match:
            await interaction.followup.send("❌ ลิงก์ไม่ถูกต้อง กรุณาตรวจสอบอีกครั้งครับ", ephemeral=True)
            return
            
        voucher_hash = match.group(1)
        api_url = f"https://gift.truemoney.com/campaign/vouchers/{voucher_hash}/redeem"
        payload = {"mobile": MY_PHONE_NUMBER, "voucher_hash": voucher_hash}
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            data = response.json()
            status = data.get("status", {}).get("code")
            
            if status == "SUCCESS":
                amount_float = float(data.get("data", {}).get("my_ticket", {}).get("amount_baht", 0))
                
                if amount_float >= 99:
                    try:
                        role = interaction.guild.get_role(TARGET_ROLE_ID)
                        if role:
                            await interaction.user.add_roles(role)
                            await interaction.followup.send(f"✅ เติมเงินสำเร็จ! ได้รับยอด **{amount_float} บาท** และได้รับยศ **{role.name}** เรียบร้อยแล้ว 🎉", ephemeral=True)
                        else:
                            await interaction.followup.send(f"✅ เติมเงินสำเร็จ {amount_float} บาท แต่ไม่พบยศในระบบ (แจ้งแอดมิน)", ephemeral=True)
                    except:
                        await interaction.followup.send(f"✅ เติมเงินสำเร็จ {amount_float} บาท แต่บอทไม่มีสิทธิ์แจกยศ (เช็กตำแหน่งยศบอทให้อยู่เหนือยศ VIP)", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ ยอดเงินไม่ถูกต้อง คุณเติมมา {amount_float} บาท แต่ราคายศคือ 99 บาทครับ", ephemeral=True)
                    
            elif status == "VOUCHER_NOT_FOUND":
                await interaction.followup.send("❌ ไม่พบซองอั่งเปา (หมดอายุหรือลิงก์ผิด)", ephemeral=True)
            elif status == "VOUCHER_OUT_OF_STOCK":
                await interaction.followup.send("❌ ซองถูกใช้ไปแล้ว หรือซองเต็ม", ephemeral=True)
            else:
                await interaction.followup.send("❌ เกิดข้อผิดพลาดในการเติมเงิน", ephemeral=True)
        except:
            await interaction.followup.send("❌ ระบบขัดข้อง กรุณาลองใหม่ภายหลัง", ephemeral=True)

class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='เติมเงิน / ซื้อยศ', style=discord.ButtonStyle.blurple, emoji='🧧')
    async def topup_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AngpaoModal())

    @discord.ui.button(label='ราคายศทั้งหมด', style=discord.ButtonStyle.gray, emoji='🛒')
    async def price_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📋 **__รายการราคายศ__**\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🌟 **ยศพิเศษ VIP 99** — ราคา **99 บาท**\n"
            "━━━━━━━━━━━━━━━━━\n"
            "✅ *กดปุ่ม 'เติมเงิน / ซื้อยศ' เพื่อกรอกซองชำระเงิน*", ephemeral=True
        )

@bot.command()
async def setupmenu(ctx):
    embed = discord.Embed(
        description=(
            "⭐ **[ CLIPVERSE ]** ⭐\n\n"
            "┃ 🧧 **ระบบซื้อยศอัตโนมัติ [ 24 ชั่วโมง ]** ✨\n\n"
            "`+ กดปุ่ม \"เติมเงิน / ซื้อยศ\" เพื่อกรอกซองอั่งเปา`\n\n"
            "`- กดปุ่ม \"ราคายศทั้งหมด\" เพื่อดูราคายศ`\n\n"
            "┃ 🔞 **ระบบออโต้ ยศเข้าตัวทันทีหลังชำระเงิน** 🔞"
        ),
        color=0x2ecc71
    )
    embed.set_footer(text="ระบบซื้อยศอัตโนมัติ | ปลอดภัย รวดเร็ว 24 ชม.")

    view = MenuView()
    view.add_item(discord.ui.Button(label='ติดต่อ', style=discord.ButtonStyle.link, url='https://discord.gg/your-invite-link', emoji='🔗'))

    await ctx.send(embed=embed, view=view)

bot.run(os.getenv("TOKEN"))
      
