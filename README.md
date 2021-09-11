# libget

## NAME
Libget - Library genesis downloader script.

## SYNOPSIS
**libget** [<ins>titles</ins>] [<ins>target dirs</ins>] [<ins>options</ins>]

## TITLES
**-b** <ins>[titles]</ins> - List book titles (case-insensitive).<br>
**-j** <ins>[titles]</ins> - List journal titles (case-insensitive).<br>
**-a** <ins>[titles]</ins> - List article titles (case-insensitive).<br>
**-c** <ins>[titles]</ins> - List comic titles (case-insensitive).<br>
**-m** <ins>[titles]</ins> - List magazine titles (case-insensitive).<br>

## TARGET DIRS
**-o** <ins>title</ins> - List output directory (insert **auto** for default dir). The number of directories must match the number of titles queued for download, unless you use **allauto** instead of **auto**.

## OPTIONS
**--set-auto** <ins>auto-dir</ins> - Set the default directory for downloads.

## EXAMPLES
Download two journals and save them in designated directories:<br>
**libget -j "ACM Transactions on Graphics" "IBM Journal of Mathematics" -o "/home/okako/jur/ACM Transactions on Graphics" "/home/okako/jur/IBM Journal of Mathematics"**<br><br>
Download two journals and save them to default directory:<br>
**libget -j "Nature" "Nurture" -o auto auto**<br>
**libget -j "Nature" "Nurture" -o autoall**
