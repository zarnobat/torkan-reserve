export function toJalali(gregorianDate) {
        var t, n, e = gregorianDate,
            i = parseInt(e.getFullYear()),
            o = parseInt(e.getMonth()) + 1,
            a = parseInt(e.getDate());
        i > 1600 ? (t = 979, i -= 1600) : (t = 0, i -= 621);
        var r = o > 2 ? i + 1 : i;
        return n = 365 * i + parseInt((r + 3) / 4) - parseInt((r + 99) / 100) + parseInt((r + 399) / 400) - 80 + a + [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334][o - 1],
            t += 33 * parseInt(n / 12053), n %= 12053, t += 4 * parseInt(n / 1461),
            (n %= 1461) > 365 && (t += parseInt((n - 1) / 365), n = (n - 1) % 365), {
            year: t,
            month: n < 186 ? 1 + parseInt(n / 31) : 7 + parseInt((n - 186) / 30),
            day: 1 + (n < 186 ? n % 31 : (n - 186) % 30)
        };
    }
export function jalaliToGregorian(jy, jm, jd) {
        var gy;
        if (jy > 979) {
            gy = 1600;
            jy -= 979;
        } else {
            gy = 621;
        }
        var days = (365 * jy) + Math.floor(jy / 33) * 8 + Math.floor(((jy % 33) + 3) / 4);
        for (var i = 0; i < jm - 1; ++i) {
            days += [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29][i];
        }
        days += jd - 1;
        gy += 400 * Math.floor(days / 146097);
        days %= 146097;
        var leap = true;
        if (days >= 36525) {
            days--;
            gy += 100 * Math.floor(days / 36524);
            days %= 36524;
            if (days >= 365) {
                days++;
            } else {
                leap = false;
            }
        }
        gy += 4 * Math.floor(days / 1461);
        days %= 1461;
        if (days >= 366) {
            leap = false;
            days--;
            gy += Math.floor(days / 365);
            days = days % 365;
        }
        var gd = days + 1;
        var sal_a = [0, 31, (leap ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        var gm;
        for (gm = 0; gm < 13; gm++) {
            if (gd <= sal_a[gm]) break;
            gd -= sal_a[gm];
        }
        return new Date(gy, gm - 1, gd);
    }

export function it(jy, jm, jd) {
    const gDate = jalaliToGregorian(jy, jm, jd);
    return gDate.getDay();
}