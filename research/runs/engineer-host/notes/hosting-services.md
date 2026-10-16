# Hosting services for the engineer host

Brief: Name hosting services with current prices per host type (VPS, cloud desktop, cloud Mac, home Mac Mini) and say which fits the blueprint best per dollar.
Run: research/runs/engineer-host/PLAN.md

All prices pulled 2026-10-16 (today). Hetzner raised cloud prices on 15 June 2026; Apple raised Mac mini prices in June and again at the M6 launch. Older price pages and blog posts are stale.

## 1. VPS providers (about 4 vCPU / 8 GB, static IP, snapshots, US East)

### Takeaway
For the blueprint (Ubuntu, headed Chrome under Xvfb/noVNC, Claude Code), the cheapest named option is Hetzner CX33 in Germany (~$10/month, but about 90 ms+ from US East, and no CX in Ashburn in the price table I read); the US East choices are Hetzner CPX31 at Ashburn ($73.49), DigitalOcean Basic 4 vCPU/8 GB ($48), Akamai/Linode 8 GB ($48 + $10 backups), Lightsail ($84 for 4 vCPU/8 GB, compute-optimized), GCP e2-standard-4 (about $98/month, 16 GB). Best per dollar in US East: DigitalOcean or Linode at $48; best overall price: Hetzner EU if latency to a noVNC session is tolerable. Confidence: medium (Vultr 4 vCPU/8 GB and Oracle A1 limits not verified).

### Cited findings
- Hetzner CX33 (4 vCPU / 8 GB) Germany/Finland is $9.99/month excl. IPv4 after the 15 June 2026 adjustment (EUR 8.49) — https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/, opened 2026-10-16, curl+parse — Quote: "CX33|0.0104 / 6.49|0.0136 / 8.49|0.0128 / 7.99|0.0160 / 9.99" (old EUR/new EUR/old USD/new USD, hourly / monthly; parsed from table HTML).
- Hetzner US (ASH/HIL) list in that table carries CCX and CPX types; CPX31 is $73.49/month excl. IPv4 after the increase — same URL, opened 2026-10-16, Parallel fetch — Quote: "|CPX31 |0.0336 / 20.99 |0.1001 / 62.49 |0.0400 / 24.99 |0.1178 / 73.49 |".
- Hetzner snapshots are manual copies kept until deleted; they survive deletion of the server — https://www.hetzner.com/cloud/cost-optimized/, opened 2026-10-16, Parallel fetch — Quote: "Snapshots are one-time, manually created copies of the server hard drive that remain permanently stored until they are actively deleted."
- Hetzner terms prohibit DDoS, open mail relays, spam and crypto mining; I found no clause against browser automation — https://www.hetzner.com/legal/terms-and-conditions/, opened 2026-10-16, Parallel fetch — Quote: "The operation of applications for mining cryptocurrencies remains prohibited."
- DigitalOcean Basic 4 vCPU / 8 GiB is $48/month; snapshots $0.06/GB/month; backups 20% (weekly) or 30% (daily) of Droplet cost; each Droplet has its own public IPv4 — https://www.digitalocean.com/pricing/droplets, opened 2026-10-16, Parallel fetch — Quote: "|Droplet Snapshots |$0.06/GB per month |"; "| 8 GiB | 4 vCPUs | 5,000 GiB | 160 GiB | $0.07143 | [$48.00]".
- Akamai/Linode 8 GB shared is 4 vCPU, 160 GB, $48/month; backups for that size $10/month — https://www.akamai.com/cloud/pricing/north-america, opened 2026-10-16, Parallel fetch — Quote: "| Linode 8 GB | $48.00 | $0.0720 | 8 GB | 4 | 160 GB | 5 TB | 40/5 Gbps |".
- Vultr stored snapshots cost $0.05/GB/month, automatic backups add 20% — https://www.vultr.com/pricing/, opened 2026-10-16, Parallel fetch — Quote: "Stored snapshots will cost $0.05/GB per month - pricing subject to change."
- AWS Lightsail: Compute Optimized 8 GB / 4 vCPU is $84/month (General Purpose 8 GB is only 2 vCPU at $44), public IPv4 included — https://aws.amazon.com/lightsail/pricing/, opened 2026-10-16, Parallel fetch — Quote: "$84 USD/mo **8 GB** Memory **4** vCPUs **320 GB** SSD Disk **6 TB** Transfer*".
- GCP e2-standard-4 (4 vCPU / 16 GiB) lists at $0.13402284/hour on-demand (about $98/month at 730 h); e2-standard-2 (2 vCPU / 8 GiB) $0.06701142/hour; us-east1/east4/east5 regions exist — https://cloud.google.com/products/compute/pricing/general-purpose, opened 2026-10-16, Parallel fetch — Quote: "|e2-standard-4 |4 |16 GiB |$0.13402284 / 1 hour".
- Oracle Always Free includes Arm Ampere A1 compute, but idle accounts can be terminated — https://www.oracle.com/cloud/free/, opened 2026-10-16, Parallel fetch — Quote: "Accounts left idle for 30 days or more may be deemed abandoned and become eligible for suspension or termination."

### Contradictions
- None found among opened pages. A third-party price list gave Hetzner CX33 as EUR 10.70 and "from EUR 7.13" (eucloudcost.com, search excerpt only, not opened) while Hetzner's own table says EUR 8.49; I used Hetzner's table.

### Inferences
- (Mine) Hetzner CPX31 is 4 vCPU/8 GB; the Hetzner page I read lists only names and prices, and the spec comes from a search excerpt of a third-party site (not opened). Check the spec before ordering.
- (Mine) 4 vCPU / 8 GB at $48 DO/Linode with snapshots on top (160 GB disk at $0.06/GB about $9.6 worst case, usually less since snapshots bill used size) lands near $55-60/month.
- (Mine) Hetzner EU at about $10 is roughly 5x cheaper than US East options; for a single user whose noVNC session is used briefly for logins, 90-100 ms latency is probably acceptable, but Google/Attio may flag a German IP at sign-in (risk, untested). Spike this.

### Gaps
- Vultr 4 vCPU / 8 GB regular or high-performance price: pricing page excerpt showed only a larger "Optimized" table; not read.
- Oracle A1 Always Free OCPU/RAM allowance and the real-world reclaim of idle instances: page excerpt did not include the numbers.
- Hetzner IPv4 per-month fee and whether CX types exist at Ashburn: not found on the pages opened.
- OVH: not researched. Provider terms against browser automation: only Hetzner's terms were opened; DO, Vultr, Akamai, AWS, GCP acceptable-use policies not opened.

## 2. Cloud desktop products

### Takeaway
Poor fit per dollar. Windows 365 Business 4 vCPU/16 GB is $56/month for a Windows desktop (the blueprint is Ubuntu), WorkSpaces AlwaysOn gives a flat monthly Linux desktop but its Ubuntu prices were not retrieved, Kasm CE is free but only for non-commercial use and 5 sessions, and Shadow is a gaming product. A $48 Linux VPS with noVNC beats all of them on price and control. Confidence: medium.

### Cited findings
- Windows 365 Business: 2 vCPU/8 GB/128 GB $36; 4 vCPU/16 GB/128 GB $56; 8 vCPU/32 GB/256 GB $108.80 per user per month — https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing, opened 2026-10-16, Parallel fetch — Quote: "Windows 365 Business 4 vCPU, 16 GB, 128 GB ... $56.00 user/month".
- Windows 365 Flex Cloud PCs (the shared/idle-limited variant) sign users out on idle and keep dedicated ones powered only two hours after the session goes inactive; this is the Flex doc, not the Business always-on plan — https://learn.microsoft.com/en-us/windows-365/enterprise/windows-365-flex-cloud-pc-session-time-limits, opened 2026-10-16, Parallel fetch — Quote: "Windows 365 Flex Cloud PCs in Dedicated mode remain powered on for two hours after the user session becomes inactive."
- Amazon WorkSpaces Personal has AlwaysOn (flat monthly, unlimited use) and AutoStop (stops after disconnect, hourly billing); a Power Ubuntu AutoStop bundle is $7.25/month + $0.66/hour — https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/, opened 2026-10-16, Parallel fetch — Quote: "AlwaysOn virtual desktops are billed at a predictable, flat monthly rate for unlimited usage".
- WorkSpaces AutoStop stops after 20 minutes without a client connection, so it would kill an unattended job — https://docs.aws.amazon.com/workspaces/latest/adminguide/running-mode.html, search excerpt of an AWS docs page only, NOT opened; moved to Gaps.
- Kasm Workspaces Community Edition is free for individuals and non-commercial use, 5 concurrent sessions; Starter is $10/user or $20/session with a license minimum below 25 — https://kasm.com/community-edition, search excerpt only (not opened); moved to Gaps.
- Shadow PC page opened is a French-language gaming landing page, mostly "cloud gaming"; no US price extracted — https://www.shadow.tech/en-us/pricing/, opened 2026-10-16, Parallel fetch — Quote: "Shadow subscriptions are mostly monthly-based."

### Contradictions
- None found.

### Inferences
- (Mine) Windows 365 runs Windows; Claude Code supports Windows 10 1809+ (see Q5), so it is possible but diverges from the Ubuntu blueprint and costs more than a $48 VPS for equal vCPU with double the RAM.
- (Mine) Whether Microsoft or AWS terms allow an unattended agent on a Cloud PC/WorkSpace was not checked; AutoStop modes (WorkSpaces) and idle limits (Windows 365 Flex) show these products are designed around a human session, so unattended overnight work needs AlwaysOn and an admin-set no-idle-limit policy.

### Gaps
- Azure Virtual Desktop pricing and Neverinstall: not researched.
- Windows 365 Business (non-Flex) idle/disconnect behaviour: only the Flex doc was opened.
- WorkSpaces Ubuntu AlwaysOn monthly price: page text did not expose the price grid.
- Kasm CE terms and WorkSpaces running-mode doc: seen in search excerpts only (https://kasm.com/community-edition, https://docs.aws.amazon.com/workspaces/latest/adminguide/running-mode.html); not opened, not cited.
- Any provider's clause on unattended agents/automation: not found.

## 3. Cloud Macs and home Mac Mini

### Takeaway
A cloud Mac costs $149-$250/month for an M4 Mac mini (MacStadium, Scaleway EUR 149), AWS EC2 Mac about $898/month because of a 24-hour dedicated-host minimum. Buying the base Mac mini M6 (16 GB / 256 GB) is $899 one-off with 4 W idle power; over 12 months that equals about $75/month, over 24 months about $37/month, plus roughly $1-3/month electricity. Buying beats renting after about 6 months of MacStadium M4.S. Confidence: high on prices, medium on break-even (ignores resale, tax, tailnet costs).

### Cited findings
- Apple: Mac mini with M6 starts at $899 (US), education $799; M5 Pro $1,699; shipping from 22 September 2026 — https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/, opened 2026-10-16, Parallel fetch — Quote: "Mac mini with M6 starts at **$899** (U.S.) and **$799** (U.S.) for education".
- Apple support power table: Mac mini M6 16 GB/256 GB idle 4 W, max 70 W; M4 idle 4 W, max 65 W — https://support.apple.com/en-gb/103253, opened 2026-10-16, Parallel fetch — Quote: "| 4 W | 70W | 14 BTU/h | 239 BTU/h |".
- Apple newsroom pitches this Mac mini for "always-on agentic computing" — same newsroom URL, opened 2026-10-16 — Quote: "supercharging the leading desktop for always-on agentic computing".
- MacStadium Mac mini monthly: M2 8 GB $109, M4 16 GB/256 GB $149, M4 24 GB/512 GB $249, M4 Pro 48 GB $349 — https://macstadium.com/pricing, opened 2026-10-16, WebFetch — Quote: "M4.S Mac mini M4 10 Core 16 GB 256 GB SSD $149" (text from the fetched table; WebFetch summarised it).
- Scaleway Mac mini M4: EUR 149/month (16 GB/256 GB), EUR 199/month (32 GB/1 TB), M4 Pro 64 GB EUR 335; hourly EUR 0.22; Paris only; 24-hour minimum; macOS only — https://www.scaleway.com/en/pricing/apple-silicon/ and https://www.scaleway.com/en/mac-mini-m4, opened 2026-10-16 — Quote: "| M4-S | Apple M4 CPU 10C / GPU 10C / Neural 16C - 4.4Ghz | 16 GB | 1 × 256 GB SSD | 1 Gbps | €149 /MONTH €0.22 /HOUR |".
- AWS EC2 Mac is billed as a dedicated host with a 24-hour minimum — https://aws.amazon.com/ec2/dedicated-hosts/pricing/, opened 2026-10-16, Parallel fetch — Quote: "On-Demand EC2 Mac Dedicated Hosts have a minimum host allocation and billing duration of 24 hours."
- mac-m4.metal costs $1.23/hour on demand (10 vCPU, 24 GiB) — https://instances.vantage.sh/aws/ec2/mac-m4.metal, search excerpt only (not opened); I use it only as a pointer: $1.23 x 730 h = about $898/month (my arithmetic). Treat AWS hourly rate as unverified against AWS.

Cost comparison (my arithmetic from the cited prices; USD, excl. tax, M4-class 16 GB unless noted):

| Option | Monthly | 12 months | 24 months |
| --- | --- | --- | --- |
| Buy Mac mini M6 16/256 ($899) + about $1-3 power | about $75-77 | about $899 + power | about $899 + power (about $38/month) |
| MacStadium M4.S | $149 | $1,788 | $3,576 |
| Scaleway M4-S (EUR 149, about $160-170, FX not checked) | about EUR 149 | EUR 1,788 | EUR 3,576 |
| AWS EC2 Mac M4 host (24 h min, unverified rate) | about $898 | about $10,800 | about $21,600 |
| For contrast: DO 4 vCPU/8 GB + snapshots | about $55-60 | about $700 | about $1,400 |

### Contradictions
- None found.

### Inferences
- (Mine) Power at 4 W idle is about 3 kWh/month; even at 20 W average and $0.20/kWh that is under $3/month, so electricity is negligible next to hardware.
- (Mine) The Mac buys only what the blueprint does not need: macOS-only tools (1Password for Claude per the registry, native-app computer use). For headed Chrome + Playwright, Linux on a $48 VPS gives the same capability for less.
- (Mine) Mac mini at $899 for 16 GB is about 19 months of a $48 VPS; cloud Mac rental breaks even against purchase at about 6 months.

### Gaps
- MacinCloud: its pricing URL returned 404 (https://www.macincloud.com/pages/pricing); third-party pages (not opened) cite $25-$49/month managed/dedicated, not cited. Always-on and Apple 24-hour lease terms for MacinCloud not verified.
- Mac mini refurbished/used price and M4 stock left over after the M6 launch: not checked.

## 4. Home hosting realities

### Takeaway
A home Mac mini or spare PC works if John accepts consumer-grade uptime and puts it on a separate network segment; remote access is solved cheaply with Tailscale (free Personal plan, non-commercial only) or Cloudflare Tunnel (outbound-only). Isolation from his personal machines is the hard part at home: needs a guest VLAN/router or a separate macOS user, which the VPS gives for free. Confidence: medium (power-cut/ISP uptime numbers not sourced).

### Cited findings
- Cloudflare Tunnel uses outbound-only connections, no publicly routable IP needed, and can have all inbound traffic blocked at the firewall — https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/, opened 2026-10-16, Parallel fetch — Quote: "a lightweight daemon in your infrastructure (`cloudflared`) creates outbound-only connections to Cloudflare's global network."
- Tailscale Personal plan is free forever, 100 devices, 3 users on the current plans page — https://tailscale.com/plans, opened 2026-10-16, Parallel fetch — Quote: "Limited to 3 users 100 devices Access nearly all of Tailscale's features Use Tailscale for free, indefinitely".
- Tailscale restricts the free plan to non-commercial use; a tailnet on a custom domain is treated as business use — https://tailscale.com/pricing?plan=personal, search excerpt only (not opened); moved to Gaps.
- Apple states Mac desktops sleep when the display is off, to be handled in System Settings > Energy — https://www.apple.com/mac-mini/, opened 2026-10-16, Parallel fetch — Quote: "To conserve energy, Mac desktops automatically sleep when the display is off."

### Contradictions
- Tailscale free tier size: plans page says "Limited to 3 users" (https://tailscale.com/plans) vs third-party pages claiming 6 users (ssdnodes, comparedge; search excerpts only). Use the vendor page; one user is within either.

### Inferences
- (Mine) Remote Control (registry) is outbound-only and gives up after about 10 minutes offline, so a home internet drop longer than that needs a restart script; a VPS's datacentre network makes this rarer.
- (Mine) John's Google sign-ins come from his home IP if the Mac sits there, which reduces login-challenge risk compared with a datacentre IP; that is an advantage of home hosting, untested.
- (Mine) If John signs into Tailscale with a work-domain email it counts as business use per Tailscale's FAQ; use a personal-email tailnet or Headscale/Cloudflare Tunnel. Check his Max usage against that rule.

### Gaps
- Home uptime figures (power cuts, ISP) and router VLAN guidance: no source opened.
- noVNC/Screen Sharing over Tailscale on macOS (Screen Sharing needs a logged-in GUI session after reboot, FileVault pre-login): not researched.

## 5. Scalability and compute-boundness

### Takeaway
The engineer is not compute-bound by the model: Claude Code's documented minimum is 4 GB RAM and the model runs at Anthropic. The local load is Chrome + Playwright + Node, so 4 vCPU / 8 GB is sensible for one to a few browser sessions; limits on parallel agents will come from Max plan usage first, not the host. Confidence: medium.

### Cited findings
- Claude Code needs 4 GB+ RAM, x64 or ARM64, macOS 13+/Windows 10 1809+/Ubuntu 20.04+ — https://code.claude.com/docs/en/setup, opened 2026-10-16, Parallel fetch — Quote: "**Hardware**: 4 GB+ RAM, x64 or ARM64 processor".
- DigitalOcean/Hetzner/Akamai resize in place (price grid rises smoothly: DO Basic 8 vCPU/16 GB $96 per a third-party page; Akamai 16 GB (6 vCPU) $96, 32 GB (8 vCPU) $192) — https://www.akamai.com/cloud/pricing/north-america, opened 2026-10-16 — Quote: "| Linode 32 GB | $192.00 | $0.2880 | 32 GB | 8 | 640 GB | 16 TB | 40/7 Gbps |".
- Windows 365 Business step-ups: 8 vCPU/32 GB $108.80 — Windows 365 URL above — Quote: "Windows 365 Business 8 vCPU, 32 GB, 256 GB ... $108.80 user/month".
- Cloud Mac rentals scale by SKU: M4 Pro 48 GB $349 at MacStadium (URL above) — Quote: "M4.L Mac mini M4 Pro 12 Core 48 GB 1 TB SSD $349".

### Contradictions
- None found.

### Inferences
- (Mine) Scaling path per type: VPS = resize or a second VPS ($48 each); cloud desktop = pick a larger SKU per user ($56 to $108.80); cloud Mac / home Mac = replace or add a second Mac ($149/month or $899). VPS grows cheapest and fastest.
- (Mine) Rough RAM rule: each headed Chrome with a heavy SaaS tab (Attio, Clay) uses on the order of 0.5-1.5 GB (my estimate, not sourced); 8 GB therefore covers Claude Code, Xvfb/noVNC and 2-3 browsers; spike this with real tabs.
- (Mine) Parallel agent count is capped by Max plan usage windows, not examined here (engineer-runtime.md covers it).

### Gaps
- Measured Chrome/Playwright memory for the Attio/Clay/n8n/Outreach tabs: not measured; belongs in a spike.
- Max plan concurrency limits: not researched in this facet.

## Recommendation (for the synthesizer)
- Default: one US-East 4 vCPU / 8 GB Ubuntu VPS at DigitalOcean or Akamai ($48 + snapshots), with Hetzner Germany (about $10) as the cheap alternative if latency and sign-in IP risk spike clean. Reasons: price, snapshots, static IP, no desktop-product idle limits.
- Home option: buy a Mac mini only if John wants macOS-only tools or a residential IP; $899 for the M6 base is under 6 months of a MacStadium rental but ~19 months of a $48 VPS.
- Reject for this blueprint: AWS EC2 Mac ($898/month, 24 h minimum), Windows 365/WorkSpaces (Windows or per-user desktop products that cost more and are built for interactive sessions), Shadow PC (gaming).
- Spike before building: (a) Google sign-in and Attio from a datacentre IP (EU and US); (b) memory use with the real SaaS tabs; (c) snapshot restore keeping Chrome logins; (d) acceptable-use policy of the chosen provider (not opened).

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Hetzner Cloud CX33 / CPX31 | https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ | VPS; CX33 4 vCPU/8 GB $9.99/mo (EU); CPX31 $73.49/mo (US ASH/HIL); manual snapshots; IPv4 extra | cloud (Germany/Finland/US) | 2026-10-16 | Cheapest; use EU if latency and IP spike pass |
| DigitalOcean Droplet (Basic 4 vCPU/8 GB) | https://www.digitalocean.com/pricing/droplets | $48/mo, snapshots $0.06/GB, backups 20-30% | cloud | 2026-10-16 | Recommended US-East default |
| Akamai Cloud / Linode 8 GB | https://www.akamai.com/cloud/pricing/north-america | 4 vCPU/8 GB $48/mo, backups $10/mo | cloud | 2026-10-16 | Equal alternative to DO |
| Vultr Cloud Compute | https://www.vultr.com/pricing/ | Snapshots $0.05/GB, backups +20%; 4 vCPU/8 GB price not read | cloud | 2026-10-16 | Unverified for the target size |
| AWS Lightsail | https://aws.amazon.com/lightsail/pricing/ | 4 vCPU/8 GB $84/mo (compute-optimized) | cloud | 2026-10-16 | Skip; pricier than DO |
| GCP Compute Engine e2 | https://cloud.google.com/products/compute/pricing/general-purpose | e2-standard-4 (16 GB) $0.134/h (about $98/mo) | cloud | 2026-10-16 | Skip; pricier |
| Oracle Cloud Free Tier | https://www.oracle.com/cloud/free/ | Always Free Ampere A1; 30-day idle termination clause | cloud | 2026-10-16 | Fallback only; reclaim risk, limits not read |
| Windows 365 Business | https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing | Windows Cloud PC: 4 vCPU/16 GB $56/mo | cloud | 2026-10-16 | Skip; Windows, interactive design |
| Amazon WorkSpaces Personal | https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/ | AlwaysOn flat monthly or AutoStop hourly Linux/Windows desktops | cloud | 2026-10-16 | Skip; AlwaysOn needed, Ubuntu price not read |
| Shadow PC | https://www.shadow.tech/en-us/pricing/ | Cloud gaming Windows PC | cloud | 2026-10-16 | Skip; gaming product, price not read |
| Kasm Workspaces CE | https://kasm.com/community-edition | Free container desktop streaming, 5 sessions, non-commercial | self-hosted | not opened (search excerpt only) | Unverified; licence may exclude commercial use |
| MacStadium | https://macstadium.com/pricing | Dedicated Mac mini M4 16 GB $149/mo | cloud | 2026-10-16 | Fallback if macOS needed without buying |
| Scaleway Mac mini M4 | https://www.scaleway.com/en/pricing/apple-silicon/ | M4-S EUR 149/mo, 24 h minimum, Paris | cloud | 2026-10-16 | Fallback; EU latency |
| AWS EC2 Mac | https://aws.amazon.com/ec2/dedicated-hosts/pricing/ | Dedicated host, 24 h minimum, about $898/mo for M4 | cloud | 2026-10-16 | Reject on cost |
| MacinCloud | https://www.macincloud.com/pages/pricing | Hosted Macs | cloud | page 404 | Unverified |
| Apple Mac mini M6 | https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/ | $899 base, 4 W idle, buy for home | home | 2026-10-16 | Home option if macOS wanted |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ | Outbound-only access to a home/VPS service | home or VPS | 2026-10-16 | Use for web access without open ports |
| Tailscale Personal | https://tailscale.com/plans | Free mesh VPN for personal use | home or VPS | 2026-10-16 | Use; check non-commercial rule |
