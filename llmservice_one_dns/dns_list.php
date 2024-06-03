<?php
# example: php dns_list.php $clouflarekey _nctu.biobank.org.tw 
# Reference: https://github.com/samejack/blog-content/blob/master/ddns/cf-ip-renew.sh#L14
# Configure: 請設定以下值
if (!isset($argv[1]) || !isset($argv[2])) exit();
#$ACCESS_TOKEN="$clouflarekey";
#$DNS_KEY="_nctu.biobank.org.tw";
$ACCESS_TOKEN=$argv[1];
$DNS_KEY=$argv[2];

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


# DNS LIST
$cmd='curl -X GET "https://api.cloudflare.com/client/v4/zones/'.$ZONE_ID.'/dns_records?per_page=1000" -H "Authorization: Bearer '.$ACCESS_TOKEN.'" -H "Content-Type: application/json"';
$cmd_All_DNS=shell_exec($cmd);
$arr=(json_decode($cmd_All_DNS, True));
$arr=$arr["result"];
$len=strlen($DNS_KEY);
for ($i=0;$i<count($arr);$i++){
 $DNS_id=$arr[$i]["id"];
 $DNS_name=trim($arr[$i]["name"]);
 if (substr($DNS_name,-$len)==$DNS_KEY){
  echo $DNS_name."\n";
 }
} 
