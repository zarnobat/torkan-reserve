import { toJalali } from "./date_functions.js";
document.addEventListener("DOMContentLoaded", function () {
    const today = new Date();
    const today_jalali = toJalali(today);
    jalaliDatepicker.startWatch({
        minDate: today_jalali,
    });

    if (window.flatpickr && flatpickr.l10ns && flatpickr.l10ns.fa) {
        flatpickr.localize(flatpickr.l10ns.fa);
    }
    const ticketTypeSelect = document.querySelector("#id_ticket_type");
    const wrappers = Array.from(document.querySelectorAll(".field-wrapper"));

    const map = {
        leave: ["leave_start", "leave_end", "leave_type"],
        facility: ["facility_amount", "facility_duration_months"],
        advance: ["advance_amount"],
        other: ["description"]
    };

    function setVisibility(selected) {
        const sel = selected || ticketTypeSelect.value || 'other';
        wrappers.forEach(w => {
            const name = w.dataset.fieldName;
            const field = w.querySelector("input, textarea, select");

            if (name === 'employee' || name === 'status' || name === 'ticket_type') {
                if (name !== 'ticket_type') {
                    w.classList.add('hidden');
                    if (field) field.required = false;
                } else {
                    w.classList.remove('hidden');
                    if (field && field.hasAttribute("data-was-required")) {
                        field.required = true;
                    }
                }
                return;
            }

            if (map[sel] && map[sel].includes(name)) {
                w.classList.remove('hidden');
                if (field && field.hasAttribute("data-was-required")) {
                    field.setAttribute("required", "required");
                }
            } else {
                w.classList.add('hidden');
                if (field) {
                    if (field.required && !field.hasAttribute("data-was-required")) {
                        field.setAttribute("data-was-required", "true");
                    }
                    field.removeAttribute("required");
                }
            }

        });
    }

    if (!ticketTypeSelect) {
        console.error("فیلد ticket_type در فرم پیدا نشد");
        return;
    }

    setVisibility(ticketTypeSelect.value);

    ticketTypeSelect.addEventListener('change', function () {
        setVisibility(this.value);
        document.querySelectorAll(".is-invalid").forEach(el => {
            el.classList.remove("is-invalid");
        });
        document.querySelectorAll(".invalid-feedback").forEach(el => {
            el.textContent = "";
        });
    });

    // تابع بهبودیافته برای فرمت سه‌رقمی
    function setupPriceInput(selector) {
        const input = document.querySelector(selector);
        if (!input) return;

        // تغییر نوع به text و استایل LTR برای سازگاری با اعداد
        input.setAttribute("type", "text");
        input.style.textAlign = "left";
        input.style.direction = "ltr";

        // فیلد مخفی برای مقدار خام (بدون کاما)
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = input.name;
        input.name = input.name + "_display";  // نام نمایش رو تغییر می‌دیم
        input.parentNode.insertBefore(hiddenInput, input.nextSibling);

        const formatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });  // کاما انگلیسی (,)
        // اگر کاما پارسی می‌خوای: const formatter = (num) => num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '،');

        // تابع برای تبدیل اعداد فارسی به انگلیسی
        function normalizeDigits(value) {
            return value.replace(/[۰-۹]/g, function (d) {
                return String.fromCharCode(d.charCodeAt(0) - 1728);  // تبدیل ۰-۹ به 0-9
            });
        }

        // تابع برای شمارش کاماها قبل از یک موقعیت خاص
        function countCommasBefore(str, pos) {
            return (str.slice(0, pos).match(/,/g) || []).length;
        }

        if (input.value) {
            let initialValue = normalizeDigits(input.value.replace(/,/g, "").trim());
            console.log("Initial value (normalized):", initialValue);  // debug: مقدار اولیه
            if (/^\d+$/.test(initialValue)) {
                input.value = formatter.format ? formatter.format(initialValue) : formatter(initialValue);
                hiddenInput.value = initialValue;
            }
        }

        input.addEventListener("input", function (e) {
            const errorElement = document.getElementById(`error-${e.target.id}`);
            const oldValue = e.target.value;
            const cursorStart = e.target.selectionStart;
            const cursorEnd = e.target.selectionEnd;

            // محاسبه موقعیت بدون کاما
            const commasBeforeStart = countCommasBefore(oldValue, cursorStart);
            const commasBeforeEnd = countCommasBefore(oldValue, cursorEnd);
            let value = normalizeDigits(oldValue.replace(/,/g, "").trim());  // normalize اعداد فارسی
            console.log("Input value (normalized):", value);  // debug: مقدار بعد از تایپ

            if (/^\d*$/.test(value)) {
                if (value !== "") {
                    const formatted = formatter.format ? formatter.format(value) : formatter(value);
                    console.log("Formatted value:", formatted);  // debug: فرمت‌شده

                    // محاسبه موقعیت جدید کرسور
                    const newStart = cursorStart + (countCommasBefore(formatted, cursorStart - commasBeforeStart) - commasBeforeStart);
                    const newEnd = cursorEnd + (countCommasBefore(formatted, cursorEnd - commasBeforeEnd) - commasBeforeEnd);

                    e.target.value = formatted;
                    hiddenInput.value = value;
                    e.target.setSelectionRange(newStart, newEnd);
                } else {
                    hiddenInput.value = "";
                }
                errorElement.classList.remove("show");
                errorElement.textContent = "";
            } else {
                value = value.replace(/\D/g, "");
                e.target.value = value ? (formatter.format ? formatter.format(value) : formatter(value)) : "";
                hiddenInput.value = value;
                errorElement.textContent = "لطفاً فقط عدد وارد کنید";
                errorElement.classList.add("show");
            }
        });
        // جلوگیری از ورود غیرعددی (انگلیسی یا فارسی)
        input.addEventListener("keypress", function (e) {
            if (!/[0-9۰-۹]/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    setupPriceInput("#id_facility_amount");
    setupPriceInput("#id_advance_amount");
    document.getElementById("ticketForm").addEventListener("submit", function () {
    });

});