'use strict';

let token = '';

class Errors extends React.Component {
	constructor(props) {
		super(props);
		this.Set = this.Set.bind(this);
	}

	Set(message) {
		let me = this.refs.me;

		me.innerHTML = message;
		if (message.length) me.setAttribute('show', '')
		else me.removeAttribute('show');
	}

	render() {
		return React.createElement('error', {ref: 'me'})
	}
}

class Login extends React.Component {
	constructor(props) {
		super(props);
		this.state = {user: '', pass: ''};

		this.handleChange = this.handleChange.bind(this);
		this.handleSubmit = this.handleSubmit.bind(this);
	}

	handleChange(event) {
		event.preventDefault();

		event.target.className=""
		this.setState({[event.target.name]: event.target.value});
	}
	handleSubmit(event) {
		event.preventDefault();

		fetch('http://localhost:5000/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(this.state)
		}).then((response) => {
			switch (response.status) {
				case 200:
					this.refs.user.className="";
					return response.json();
				case 403:
					this.refs.pass.className="wrong";
					break;
				case 404:
					this.refs.user.className="wrong";
					break;
				default:
					throw new Error('Unexpected error occurred');
			}
		}).then((body) => {
			this.setError();
			token = body;
            this.setState(this.state);
		}).catch((err) => {
			let msg = err.message;
			if (err instanceof TypeError) {
				msg = "Could not connect to server";
			}
			this.setError(msg);
		});
	}

	setError(message) {
		if (!message) message = '';
		this.refs.errors.Set(message);
	}

	render() {
        if(!token) {
            return React.createElement('form', {id: 'login', onSubmit: this.handleSubmit},
                React.createElement('h1', null, 'Login'),
                React.createElement(Errors, {ref: "errors", class: 'hidden'}),
                React.createElement('input', {type: "text", name: "user", placeholder: "Username", onChange: this.handleChange, ref: "user"}),
                React.createElement('input', {type: "password", name: "pass", placeholder: "Password", onChange: this.handleChange, ref: "pass"}),
                React.createElement('div', {className: "right"}, 
                    React.createElement('input', {type: "submit", value: "Login"})
                )
            );
        } else {
            return React.createElement(Tests);
        }
	}
}

class Tests extends React.Component {
    constructor(props) {
        super(props);
    }
    
    componentDidMount() {
        fetch('http://localhost:5000/tests/mine', {
			method: 'GET',
            headers: {
				'Content-Type': 'application/json',
				'Token': token
            }
        }).then(function (response) {
            console.log(response);
        })
    }
  
    render() {
        return (
			React.createElement('div', null, 
                React.createElement('h1', null, 'Tests')
            )
        );
    }
}

ReactDOM.render(React.createElement(Login, null), document.getElementById("page"));
