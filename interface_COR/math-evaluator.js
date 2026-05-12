/**
 * ================================================================
 * COR ENGINE — Math Evaluator (вычисления в полях ввода)
 * ================================================================
 * 
 * ОРИЕНТИРЫ:
 * - Blender: ввод выражений в поля (10+5/2 → 12.5)
 * - Google Search: математические выражения в строке
 * - Figma: арифметика в полях размеров
 * 
 * ЧТО МЫ ИЗБЕГАЕМ:
 * - eval() без фильтрации (опасно!)
 * - Блокировки UI во время вычислений
 * 
 * К ЧЕМУ СТРЕМИМСЯ:
 * - Поддержка + - * / ( ) ** %
 * - Тригонометрия: sin, cos, tan
 * - Авто-вычисление при потере фокуса
 * - История вычислений
 * ================================================================
 */

'use strict';

/**
 * Безопасный вычислитель математических выражений.
 * 
 * Поддерживает:
 * - Базовые операции: + - * / ** %
 * - Скобки: ( )
 * - Функции: sin, cos, tan, sqrt, abs, round, floor, ceil
 * - Константы: PI, E
 * 
 * Примеры:
 *   evalMath("10+5")     → 15
 *   evalMath("10+5/2")   → 12.5
 *   evalMath("sin(PI/2)") → 1
 *   evalMath("sqrt(16)+2") → 6
 *
 * @param {string} expr - математическое выражение
 * @returns {number|null} - результат или null при ошибке
 */
function evalMath(expr) {
    if (!expr || typeof expr !== 'string') return null;

    // Убираем пробелы
    expr = expr.trim();
    if (!expr) return null;

    // Если это просто число — возвращаем его
    if (/^-?\d+\.?\d*$/.test(expr)) {
        return parseFloat(expr);
    }

    // Список разрешённых функций и констант
    const allowedFunctions = ['sin', 'cos', 'tan', 'sqrt', 'abs', 'round', 'floor', 'ceil', 'log', 'exp'];
    const allowedConstants = { PI: Math.PI, E: Math.E };

    try {
        // Заменяем константы
        let processed = expr;
        for (const [name, value] of Object.entries(allowedConstants)) {
            processed = processed.replace(new RegExp(`\\b${name}\\b`, 'g'), value);
        }

        // Проверяем что выражение содержит только разрешённые символы
        // Разрешено: цифры, операторы, скобки, точка, функции
        const allowedPattern = /^[\d+\-*/().%\s,]+$/;
        const funcPattern = new RegExp(`\\b(${allowedFunctions.join('|')})\\b`, 'g');

        // Временно убираем функции для проверки
        const withoutFuncs = processed.replace(funcPattern, '');

        if (!allowedPattern.test(withoutFuncs.replace(/\s+/g, ''))) {
            console.warn('⚠️ Недопустимые символы в выражении:', expr);
            return null;
        }

        // Создаём безопасную функцию
        const funcBody = `return (${processed})`;
        const result = new Function(funcBody)();

        // Проверяем что результат — конечное число
        if (typeof result !== 'number' || !isFinite(result)) {
            console.warn('⚠️ Результат не является конечным числом:', expr, '→', result);
            return null;
        }

        return result;

    } catch (e) {
        console.warn('⚠️ Ошибка вычисления:', expr, e.message);
        return null;
    }
}

/**
 * Делает поле ввода "умным" — вычисляет выражение при потере фокуса.
 * 
 * Использование:
 *   makeInputSmart(document.getElementById('pos-x'));
 *   // Или для всех полей:
 *   document.querySelectorAll('.coord-input').forEach(makeInputSmart);
 *
 * @param {HTMLInputElement} input - поле ввода
 */
function makeInputSmart(input) {
    if (!input || input.dataset.mathEnabled) return;

    input.dataset.mathEnabled = 'true';

    // Сохраняем оригинальное значение для сброса по Escape
    let originalValue = input.value;

    input.addEventListener('focus', () => {
        originalValue = input.value;
    });

    input.addEventListener('blur', () => {
        const expr = input.value.trim();
        const result = evalMath(expr);

        if (result !== null && result !== parseFloat(originalValue)) {
            // Округляем до 4 знаков
            const rounded = Math.round(result * 10000) / 10000;
            input.value = rounded;

            // Визуальная индикация
            input.style.borderColor = 'var(--success)';
            setTimeout(() => {
                input.style.borderColor = '';
            }, 600);

            console.log(`🧮 ${expr} → ${rounded}`);

            // Вызываем событие изменения
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });

    input.addEventListener('keydown', (e) => {
        // Enter = вычислить и перейти к следующему полю
        if (e.key === 'Enter') {
            e.preventDefault();
            input.blur();

            // Фокус на следующее поле
            const allInputs = Array.from(document.querySelectorAll('.coord-input, input[type="text"]'));
            const currentIndex = allInputs.indexOf(input);
            if (currentIndex < allInputs.length - 1) {
                allInputs[currentIndex + 1].focus();
                allInputs[currentIndex + 1].select();
            }
        }

        // Escape = вернуть оригинальное значение
        if (e.key === 'Escape') {
            input.value = originalValue;
            input.blur();
        }
    });
}

/**
 * Применить умные поля ко всем координатным инпутам на странице.
 * Вызывать после загрузки DOM.
 */
function enableAllSmartInputs() {
    document.querySelectorAll('.coord-input').forEach(makeInputSmart);
    document.querySelectorAll('input[type="text"]:not(#geometry-search):not(#chat-input)').forEach(input => {
        // Только для числовых полей
        if (input.closest('.inspector-row') || input.closest('.inspector-section')) {
            makeInputSmart(input);
        }
    });
    console.log('🧮 Умный ввод активирован для всех полей');
    console.log('   Примеры: 10+5 → 15 | 50/2 → 25 | sin(PI/2) → 1');
    console.log('   Enter = вычислить, Escape = отмена');
}

// Экспорт для модульного использования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { evalMath, makeInputSmart, enableAllSmartInputs };
}