export function getErrorMessage(err, defaultMessage) {
    if (!defaultMessage) defaultMessage = 'An unexpected error occurred. Try again.';
    if (!err || !err.response || !err.response.data) {
        return defaultMessage;
    }

    const detail = err.response.data.detail;

    if (typeof detail === 'string') {
        return detail;
    }

    // Handle FastAPI validation error format (array of objects)
    if (Array.isArray(detail) && detail.length > 0) {
        // Extract the message from the first validation error
        const firstError = detail[0];
        if (firstError.msg) {
            return firstError.msg;
        }
        // Fallback if it's an array of strings
        if (typeof firstError === 'string') {
            return firstError;
        }
    }

    return defaultMessage;
}
