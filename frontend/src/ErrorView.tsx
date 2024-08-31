import { Component } from "solid-js"

interface ErrorViewProps {
    Error: Error
}

const ErrorView: Component<ErrorViewProps> = (props: ErrorViewProps) => {
    return (
        <div class="error-view">
            <h1>
                Error: {props.Error.message}
            </h1>
            {
                props.Error.stack ?? ""
            }
        </div>
    );
}

export default ErrorView