param(
    [string]$AlphaPoseLocation,
    [string]$VideoPath
)

# Sets working directory to AlphaPose in order to process the video
Set-Location $AlphaPoseLocation

python process_video.py --cfg configs/halpe_26/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/halpe26_fast_res50_256x192.pth --video $VideoPath --save_video
