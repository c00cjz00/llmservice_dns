# 注意: 請先 先編集 env.sample 內容
# Example: ./01-init.sh $clouflarekey ntuh 211.73.81.102 gpu
[[ -z "$1" ]] && { echo "Parameter 1 is empty" ; exit 1; }
[[ -z "$2" ]] && { echo "Parameter 2 is empty" ; exit 2; }
[[ -z "$3" ]] && { echo "Parameter 3 is empty" ; exit 3; }
[[ -z "$4" ]] && { echo "Parameter 4 is empty" ; exit 4; }
Cloudflare_KEY=$1
DNS=$2
INTERNET_IP=$3
IS_GPU=$4

# 目前位置
mypwd=$(pwd)

# ENV
cp env.sample .env

# DNS (請修改DNS, INTERNET_IP)
IP_Tmp="${INTERNET_IP//./}"
IP=${IP_Tmp: -4}
IP="2"
rsync -av nginx_conf/ nginx
sed -i "s/_nchc.biobank.org.tw/${IP}${DNS}.biobank.org.tw/g" nginx/*conf


# Create Website 
rsync -av website_conf/ website
sed -i "s/_nchc.biobank.org.tw/${IP}${DNS}.biobank.org.tw/g" website/index.php	

# Create litellm 
rsync -av litellm_conf/ litellm

# Create juicer 
rsync -av juicer_conf/ juicer


# 建立目錄
cd ${mypwd}
mkdir -p storage/anythingllm_data
mkdir -p storage/anythingllm_hotdir 
mkdir -p storage/anythingllm_outputs 
mkdir -p storage/ollama_data 
mkdir -p storage/openwebui_data 
mkdir -p storage/hf_cache 
mkdir -p storage/postgres
mkdir -p storage/pgadmin
chmod 777 storage/pgadmin
mkdir -p storage/factory_data storage/factory_saves storage/factory_cache storage/jupyter_data
mkdir -p storage/output
mkdir -p storage/mergekit_tmp
mkdir -p storage/juicer_cache
cp factory_conf/data/dataset_info.json storage/factory_data/
cp factory_conf/data/identity.json storage/factory_data/
cp factory_conf/data/alpaca_en_demo.json storage/factory_data/
cp factory_conf/data/c4_demo.json storage/factory_data/
rsync -avHS factory_conf/ factory
rsync -avHS factory_conf/examples/ storage/factory_examples
rsync -avHS notebook_conf/ storage/jupyter_data/notebook
rsync -avHS mergekit_conf/ mergekit
 
if ! [ -f ./storage/anythingllm_env.txt ]; then
	touch ./storage/anythingllm_env.txt
fi 

if ! [ -f ./.env ]; then
	cp ./env.sample .env
fi

 
# Cloudflare 設定 
#DNS_KEY=${IP}${DNS}.biobank.org.tw
DNS_KEY=${DNS}.biobank.org.tw
php dns_delete.php $Cloudflare_KEY $DNS_KEY
sleep 10
php dns_add.php $Cloudflare_KEY $DNS $INTERNET_IP


# 複製compsoe file
# CPU/GPU
if [[ "$IS_GPU" == "gpu" ]] 
then
	cp compose/docker-compose_gpu.yml docker-compose.yml
else
	cp compose/docker-compose_cpu.yml docker-compose.yml
fi

# echo 
echo PORTAL: https://portal${IP}${DNS}.biobank.org.tw

