<?php
# example: php dns_add.php $clouflarekey nyu 211.73.81.102
# Reference: https://github.com/samejack/blog-content/blob/master/ddns/cf-ip-renew.sh#L14
# Configure: 請設定以下值
#[[ -z "$1" ]] && { echo "Parameter 1 is empty" ; exit 1; }

if (!isset($argv[1]) || !isset($argv[2]) || !isset($argv[3])) exit();
#$ACCESS_TOKEN="$clouflarekey";
#$HOSTNAME_KEY="nyu";
#$INTERNET_IP="211.73.81.102";  
$ACCESS_TOKEN=$argv[1];
$HOSTNAME_KEY=$argv[2];
$INTERNET_IP=$argv[3];  
$HOSTNAME_Arr=array("portal","anythingllm","openwebui","litellm","pgadmin4","factory","llmbook","mergekit");

# 確認是否能連線成功
$cmd='curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type:application/json" |jq';
$check_ACCESS_TOKEN=shell_exec($cmd);

# 確認連線區域取得ZONE_ID
$cmd='curl -X GET "https://api.cloudflare.com/client/v4/zones" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type:application/json" |jq';
$check_ZONE_ID=shell_exec($cmd);
#echo $check_ZONE_ID."\n";
$arr=(json_decode($check_ZONE_ID, True));
$ZONE_ID=$arr["result"][0]["id"];

# 單一DNS資訊
#$cmd='curl -X GET "https://api.cloudflare.com/client/v4/zones/'.$ZONE_ID.'/dns_records" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type:application/json" |jq';
#$check_RECORD_ID=shell_exec($cmd);
#echo $check_RECORD_ID."\n";
#$cmd_update_DNS='curl -X PUT "https://api.cloudflare.com/client/v4/zones/'.$ZONE_ID.'/dns_records/'.$RECORD_ID.'" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type: application/json" --data \'{"type":"A","name":"'.$DNS.'","content":"'.$INTERNET_IP.'","ttl":120,"proxied":false}\'';


# 新增DNS
for ($i=0;$i<count($HOSTNAME_Arr);$i++){
 $short_ip=substr(str_replace('.','',$INTERNET_IP),-4);
 $short_ip="";
 $myDNS=$HOSTNAME_Arr[$i].$short_ip.$HOSTNAME_KEY;   
 $cmd_create_DNS='curl -X POST "https://api.cloudflare.com/client/v4/zones/'.$ZONE_ID.'/dns_records" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type: application/json" --data \'{"type":"A","name":"'.$myDNS.'","content":"'.$INTERNET_IP.'","ttl":120,"proxied":false}\'';
 echo shell_exec($cmd_create_DNS);
 echo $cmd_create_DNS."\n";
}
