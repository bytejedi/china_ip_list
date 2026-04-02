**IPList for China by IPIP.NET**

鉴于众所周知，不用言传你也能意会的理由，我们制作了这份针对于中国大陆地区的 IP 列表。供大家使用。

**有几点说明：**

1、一般每季度更新一次。

2、本数据并非完全基于路由表数据生成，IP WHOIS 信息中标注为中国但未做 BGP 公告的数据，也会被列入。

3、因更新频度限制，不对其数据质量做任何承诺，但有问题，可以去我们的 QQ 群反馈，我们根据情况考虑应急更新。

4、我们认为，每天都有 IP 在变动，所以即使有不准的情况，在按季度的更新周期下是正常的情况，如果您有快速更新数据的需求，请与我们联系。

5、为减少条目数量，国内外的运营商骨干网部分 IP 均可能会做模糊化处理，但不影响正常使用。

6、如果觉得我们做的还不错，希望帮忙宣传和支持我们的主力业务。

7、有些多 WAN 口路由器和防火墙设备有 ISP 文件的需求，我们愿意与厂商合作，由我们来提供这个看着细小但实际上很影响用户体验但对我们来说相对轻松的数据，合作形式多样，有兴趣，请与我们联系。sales@ipip.net

8、IP 地理位置数据库相关讨论 QQ 群: 346280296。

9、本数据使用 CC-BY-NC-SA 4.0 授权许可。

**WireGuard AllowedIPs 生成工具：**

将 `0.0.0.0/0` 减去中国 IP 段，生成 WireGuard AllowedIPs 配置（非中国流量走隧道）。

**基本用法：**

```bash
python3 generate_allowed_ips.py
```

默认读取同目录下的 `china_ip_list.txt`，输出到 `allowed_ips.txt`（逗号分隔的 CIDR 列表）。

**跳过额外网段（`--skip`）：**

使用 `--skip` 指定不走隧道的额外 CIDR 段（如内网、保留地址等）：

```bash
# 跳过单个网段
python3 generate_allowed_ips.py --skip 192.168.0.0/16

# 跳过多个网段
python3 generate_allowed_ips.py --skip 192.168.0.0/16 172.16.0.0/12 169.254.0.0/16
```

常见可跳过的网段：

| CIDR | 说明 |
|------|------|
| `10.0.0.0/8` | A 类私有地址（若 WireGuard 使用 10.x 子网则不要跳过） |
| `172.16.0.0/12` | B 类私有地址 |
| `192.168.0.0/16` | C 类私有地址 |
| `100.64.0.0/10` | 运营商级 NAT（CGNAT） |
| `127.0.0.0/8` | 回环地址 |
| `169.254.0.0/16` | 链路本地地址 |
| `224.0.0.0/4` | 组播地址 |
| `240.0.0.0/4` | 保留地址 |

**自定义输出路径（`-o` / `--output`）：**

```bash
python3 generate_allowed_ips.py -o my_allowed.txt
python3 generate_allowed_ips.py --skip 192.168.0.0/16 -o /etc/wireguard/allowed.txt
```

**IP 查询（`--lookup`）：**

查询 IP 是否属于中国 IP 段，输出匹配的子网（若无输出则不在中国 IP 段内，流量将走隧道）：

```bash
# 查询单个 IP
python3 generate_allowed_ips.py --lookup 114.114.114.114

# 查询多个 IP
python3 generate_allowed_ips.py --lookup 8.8.8.8 1.1.1.1 192.168.1.1
```

**写入 WireGuard 配置文件（macOS）：**

```bash
sed -i '' "s|^AllowedIPs = .*|AllowedIPs = $(cat allowed_ips.txt)|" /etc/wireguard/wg0.conf
```

**查看完整帮助：**

```bash
python3 generate_allowed_ips.py --help
```

**相关链接：**

1、[IP 地址库试用版下载](https://www.ipip.net/ipdb.html "IPIP.NET IP 归属地数据库")

2、[IPIP.NET 网络工具集](https://tools.ipip.net/traceroute.php "IPIP.NET 网络工具集") 目前由我和同事在维护的，全球有超过 600 多个监测点可供使用，traceroute 功能尤其强大和准确，是你 ping 检测和 traceroute 路径分析的好帮手。

3、[Best Trace 工具](https://www.ipip.net/download.html#ip_trace "Best Trace 工具") 如果你想了解本机发起的 traceroute 情况，并且有地理路径地图可视化需求，请使用我们这个工具，备受好评哦。
