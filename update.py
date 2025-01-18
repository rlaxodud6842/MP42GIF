import asyncio
import time
import discord
from discord.ext import commands
from discord import app_commands
import requests
from moviepy.editor import VideoFileClip
import os
from moviepy.video.fx import all as vfx
from dotenv import load_dotenv


load_dotenv(verbose=True)
BOT_TOKEN = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)
intents = discord.Intents.default()  # 기본 인텐트 설정
intents.message_content = True  # 메시지 내용 인텐트 활성화

@bot.tree.command(name='링크변환', description='링크 기반으로 MP4를 GIF확장자로 변환합니다')  # 명령어 이름, 설명
@app_commands.describe(url='URL')  # 같이 쓸 내용들
async def hello(interaction: discord.Interaction, url: str):  # 출력
    await interaction.response.send_message("비디오 변환 중... 잠시만 기다려 주세요.", ephemeral=True)
    try:
        # 비디오 다운로드
        video_response = requests.get(url)
        with open("temp_video.mp4", 'wb') as f:
            f.write(video_response.content)
            f.close()

        
        
        # 비디오를 GIF로 변환
        clip = VideoFileClip("temp_video.mp4")
        
        if clip.fps > 10:
            clip = clip.fx(vfx.speedx, factor=2)  # 2배 속도 증가    
            
        if clip.duration < 1:
            clip = vfx.speedx(clip, factor=0.5) # 영상 늘리고
            clip = clip.fx(vfx.speedx, factor=1.4) # 빠르게 만들기
            
        clip = clip.subclip(0, min(7, clip.duration))  # 최대 5초로 자르기
        clip.write_gif("output.gif")
        
        # 변환된 GIF를 전송
        with open("output.gif", "rb") as f:
            await interaction.followup.send(file=discord.File(f, "output.gif"), ephemeral=True)
            f.close()

    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {e}", ephemeral=True)
    
    clip.close()
    # 비동기적으로 파일 정리
    asyncio.create_task(clean_up_files())

async def clean_up_files():
    # 정리해야 할 파일 목록
    files_to_clean = ["./temp_video.mp4", "./output.gif"]

    for file_path in files_to_clean:
        if os.path.exists(file_path):
            while True:
                try:
                    os.remove(file_path)
                    print(f"{file_path} 삭제 완료.")
                    break
                except PermissionError:
                    print(f"{file_path} 삭제 대기 중...")
                    await asyncio.sleep(0.5)  # 0.5초 후 재시도

        
    
    # await interaction.response.send_message(f'{interaction.user.mention} : {text1} : {text2}', ephemeral=True)
    
@bot.tree.command(name="파일변환", description="MP4 파일을 업로드하여 GIF로 변환하여 보내기")
@discord.app_commands.describe(file="MP4 파일")
async def hello(interaction: discord.Interaction, file: discord.Attachment):
    
        
    try:
        file_path = "temp_video.mp4"
        await file.save(file_path)
        
        if clip.fps > 10:
            clip = clip.fx(vfx.speedx, factor=2)  # 2배 속도 증가    
            
        if clip.duration < 1:
            clip = vfx.speedx(clip, factor=0.5) # 영상 늘리고
            clip = clip.fx(vfx.speedx, factor=1.4) # 빠르게 만들기

        # 비디오를 GIF로 변환
        clip = VideoFileClip("temp_video.mp4")
        clip = clip.subclip(0, min(5, clip.duration))  # 최대 5초로 자르기
        clip.write_gif("output.gif")
        

        # 디스코드에 GIF 업로드
        with open("output.gif", "rb") as f:
            message = await interaction.response.send_message(file=discord.File(f, "output.gif"),ephemeral=True)
            f.close()
        
        
    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {e}", ephemeral=True)

    finally:
        time.sleep(10)
        # 파일 정리
        # 기존 파일 삭제
        if os.path.exists("./temp_video.mp4"):
            os.remove("./temp_video.mp4")
        if os.path.exists("./output.gif"):
            os.remove("./output.gif")
    

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # 명령어 동기화
        print("슬래시 명령어가 동기화되었습니다.")
    except Exception as e:
        print(f"슬래시 명령어 동기화 중 오류 발생: {e}")
    print(f"봇 준비 완료: {bot.user}")


bot.run(BOT_TOKEN)
