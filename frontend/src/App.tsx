import React from 'react';
import { UsersTable } from './components/user/UserTable';
import { User as UserModel } from './models/User';
import { AppState } from './models/AppState';

const json_headers = {'Content-Type': 'application/json'};

const App: React.FC = () => {
  const [state, setState] = React.useState<AppState>({ users: [], error: null });

  React.useEffect(() => {
      fetch("http://localhost:5000/api/users")
          .then(response => response.json())
          .then(data => setState({...state, users: data}))
          .catch(error => setState({...state, error: error.toString()}));
  }, []);

    const handleSave = (updatedUser: UserModel) => {
        fetch(`http://localhost:5000/api/users/${updatedUser.user_id}`, {method: "PUT", headers: json_headers, body: JSON.stringify({name: updatedUser.name})})
            .then(response => response.json())
            .then(data => setState(prevState => {
                const updatedUsers = prevState.users.map(user =>
                    user.user_id===updatedUser.user_id ? {...user, name: updatedUser.name} : user
                );
                return { ...prevState, users: updatedUsers};
            }))

      // Implement saving logic here, e.g., PUT request to the server
      // Update local state after successful save
    //   updatedUser.name
  };

  const handleCancel = (id: number) => {
      // Restore original name
      const updatedUsers = state.users.map((user: UserModel) =>
          user.user_id === id ? { ...user, name: user.originalName } : user
      );
      setState({...state, users: updatedUsers});
  };

  return (
      <div className="App">
          <UsersTable users={state.users} onSave={handleSave} onCancel={handleCancel} />
      </div>
  );
}

export default App;
