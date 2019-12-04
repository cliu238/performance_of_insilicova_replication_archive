@SET /a PORT=8888
docker build -t insilico .

:LAUNCH
docker run -it -p %PORT%:8888 -v %cd%:/home/insilico/insilico insilico

@if %errorlevel% NEQ 0 (
  @SET /a PORT+=1
  @GOTO :LAUNCH
)
