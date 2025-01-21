import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import requests
from moviepy.editor import VideoFileClip
import os
from moviepy.video.fx import all as vfx
from dotenv import load_dotenv
import random
import string

load_dotenv(verbose=True)
BOT_TOKEN = os.getenv('BOT_TOKEN')


min_fps_for_speed_up = 10
min_duration_for_extend_file = 1
max_video_size = 10485760
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
        
        #랜덤 id 부여
        temp_video_id = "".join([random.choice(string.ascii_letters) for _ in range(10)])
        temp_video = temp_video_id + ".mp4"
         
        with open(temp_video, 'wb') as f:
            f.write(video_response.content)
            f.close()
        
        #용량이 10MB 이상이면 용량제한 메세지 전송
        temp_video_size = os.path.getsize(os.path.join("./",temp_video))
        if temp_video_size >= max_video_size:
            await interaction.followup.send(file=discord.File(f, temp_video_id+".gif"))
            asyncio.create_task(clean_up_files(temp_video_id))
        else:
            # 비디오를 GIF로 변환
            clip = VideoFileClip(temp_video)
            
            if clip.fps > min_fps_for_speed_up:
                clip = clip.fx(vfx.speedx, factor=2)  # 2배 속도 증가    
                
            if clip.duration < min_duration_for_extend_file:
                clip = vfx.speedx(clip, factor=0.5) # 영상 늘리고
                clip = clip.fx(vfx.speedx, factor=1.45) # 빠르게 만들기
                
            clip = clip.subclip(0, min(7, clip.duration)) 
            clip.write_gif(temp_video_id+".gif")
            
            # 변환된 GIF를 전송
            with open(temp_video_id+".gif", "rb") as f:
                await interaction.followup.send(file=discord.File(f, temp_video_id+".gif"))
                f.close()
    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {e}", ephemeral=True)
    clip.close()
    # 비동기적으로 파일 정리
    asyncio.create_task(clean_up_files(temp_video_id))
    
@bot.tree.command(name="파일변환", description="MP4 파일을 업로드하여 GIF로 변환하여 보내기")
@discord.app_commands.describe(file="MP4 파일")
async def hello(interaction: discord.Interaction, file: discord.Attachment):
    
        
    try:
        temp_video_id = "".join([random.choice(string.ascii_letters) for _ in range(10)])
        temp_video = temp_video_id + ".mp4"
                
        await file.save(temp_video)
        #용량이 10MB 이상이면 용량제한 메세지 전송
        temp_video_size = os.path.getsize(os.path.join("./",temp_video))
        if temp_video_size >= max_video_size:
            await interaction.followup.send(file=discord.File(f, temp_video_id+".gif"), ephemeral=True)
            asyncio.create_task(clean_up_files(temp_video_id))
        else:
            if clip.fps > min_fps_for_speed_up:
                clip = clip.fx(vfx.speedx, factor=2)  # 2배 속도 증가    
                
            if clip.duration < min_duration_for_extend_file:
                clip = vfx.speedx(clip, factor=0.5) # 영상 늘리고
                clip = clip.fx(vfx.speedx, factor=1.45) # 빠르게 만들기

            # 비디오를 GIF로 변환
            clip = VideoFileClip(temp_video_id+".mp4")
            clip = clip.subclip(0, min(5, clip.duration))  # 최대 5초로 자르기
            clip.write_gif(temp_video_id+".gif")
            

            # 디스코드에 GIF 업로드
            with open(temp_video_id+".gif", "rb") as f:
                message = await interaction.response.send_message(file=discord.File(f, temp_video_id+".gif"),ephemeral=True)
                f.close()
    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {e}", ephemeral=True)
    asyncio.create_task(clean_up_files(temp_video_id))
        
        

async def clean_up_files(temp_video_id):
    # 정리해야 할 파일 목록
    base_path = "./"
    temp_video_path = os.path.join(base_path, temp_video_id)
    
    files_to_clean = [temp_video_path + ".mp4", temp_video_path +".gif"]
    max_retries = 10  # 최대 재시도 횟수
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            for attempt in range(max_retries):
                try:
                    os.remove(file_name)
                    print(f"{file_name} 삭제 완료.")
                    break
                except PermissionError:
                    print(f"{file_name} 삭제 대기 중... 재시도 {attempt + 1}/{max_retries}")
                    await asyncio.sleep(0.5)
            else:
                print(f"{file_name} 삭제 실패: 다른 프로세스에서 사용 중이거나 권한 문제 발생.")

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # 명령어 동기화
        print("슬래시 명령어가 동기화되었습니다.")
    except Exception as e:
        print(f"슬래시 명령어 동기화 중 오류 발생: {e}")
    print(f"봇 준비 완료: {bot.user}")

bot.run(BOT_TOKEN)
