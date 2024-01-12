// import Image from 'next/image'

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

const secondsToTime = (seconds:number) => {
    const minutes = seconds / 60;
    const final_seconds = Math.floor(seconds % 60);
    const hours = minutes / 60;
    const final_minutes = Math.floor(minutes % 60);
    const final_hours = Math.floor(hours);

    const pad = (num:number) => num.toString().padStart(2, '0');

    return <>{pad(final_hours)}:{pad(final_minutes)}:{pad(final_seconds)}</>;
};

class ExtendedDate extends Date {
    addSeconds(seconds: number, startDate?: Date): ExtendedDate {
        const start = startDate || this;
        const final_time = start.getTime() + seconds * 1000;
        return new (this.constructor as typeof ExtendedDate)(final_time);
    }

    toTimeStringHHMMSS(): string {
        const hours = this.getHours().toString();
        const minutes = this.getMinutes().toString().padStart(2, '0');
        const seconds = this.getSeconds().toString().padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }
}

export default function CountdownPage() {
    const searchParams = useSearchParams();
    const sp_seconds = searchParams?.get('seconds');

    const [seconds, setSeconds] = useState(0);
    const [countingUp, setCountingUp] = useState(false);
    const [finishTimeStr, setFinishTimeStr] = useState("");

    // once the page loads and we get control, parse and set seconds
    useEffect(() => {
        if (sp_seconds) {
            const seconds_number = parseInt(sp_seconds||'0')||0;
            setSeconds(seconds_number);
            setCountingUp(false);

            const now = new ExtendedDate();
            const futureExtendedDate = now.addSeconds(seconds_number);
            setFinishTimeStr(futureExtendedDate.toTimeStringHHMMSS());

        }
    }, [sp_seconds]);

    // once seconds is set, start the count interval
    useEffect(() => {
        const count_interval = setInterval(() => {
            setSeconds(sec => {
                if (!countingUp && sec-1<0) {
                    setCountingUp(true);
                    return sec+1;
                }
                else if (countingUp) return sec+1;
                else return sec-1;
            });
        }, 1000);
        return () => clearInterval(count_interval);
    }, [countingUp]);

    return (
        <main>
            <div>
                {secondsToTime(seconds)}{countingUp?"+":"-"} (Finish{countingUp&&"ed"} {finishTimeStr})
            </div>
        </main>
    )
}
