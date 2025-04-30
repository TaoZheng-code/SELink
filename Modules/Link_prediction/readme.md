# LinkGenerator
cd LinkGenerator
python run_LinkGenerator.py

# Dstill
cd Dstill
python bertdistill.py

# models
cd models
train
python train.py --tra_batch_size 16 --val_batch_size 16 --end_epoch 400 --output_model <model_save_path> 

test
python test.py --tes_batch_size 16 --model_path <model_path> 