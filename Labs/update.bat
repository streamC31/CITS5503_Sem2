@echo off
REM 切换到main分支
git checkout master

REM 拉取上游更新
git pull upstream master

REM 切换回工作分支
git checkout my_work

REM 合并更新
git merge master

REM 暂停以查看合并结果
pause
