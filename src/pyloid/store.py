from pickledb import PickleDB
from typing import Any, List, Optional


class Store:
    def __init__(self, path: str):
        """
        Initialize a Store instance.

        Parameters
        ----------
        path: str
            Path to the database file where data will be stored

        Examples
        --------
        >>> store = Store("data.json")
        """
        self.db = PickleDB(path)

    def get(self, key: str) -> Any:
        """
        Retrieve the value associated with the specified key.

        Parameters
        ----------
        key: str
            The key to look up in the database

        Returns
        -------
        Any
            The value associated with the key, or None if the key doesn't exist

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("user", {"name": "John Doe", "age": 30})
        True
        >>> user = store.get("user")
        >>> print(user)
        {'name': 'John Doe', 'age': 30}
        >>> print(store.get("non_existent_key"))
        None
        """
        return self.db.get(key)

    def set(self, key: str, value: Any) -> bool:
        """
        Add or update a key-value pair in the database.

        Parameters
        ----------
        key: str
            The key to set in the database
        value: Any
            The value to associate with the key (must be a JSON-serializable Python data type)

        Returns
        -------
        bool
            Always returns True to indicate the operation was performed

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("settings", {"theme": "dark", "notifications": True})
        True
        >>> store.set("counter", 42)
        True
        >>> store.set("items", ["apple", "banana", "orange"])
        True
        """
        return self.db.set(key, value)

    def remove(self, key: str) -> bool:
        """
        Delete the value associated with the key from the database.

        Parameters
        ----------
        key: str
            The key to remove from the database

        Returns
        -------
        bool
            True if the key was deleted, False if the key didn't exist

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("temp", "temporary data")
        True
        >>> store.remove("temp")
        True
        >>> store.remove("non_existent_key")
        False
        """
        return self.db.remove(key)

    def all(self) -> List[str]:
        """
        Retrieve a list of all keys in the database.

        Returns
        -------
        List[str]
            A list containing all keys currently stored in the database

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("key1", "value1")
        True
        >>> store.set("key2", "value2")
        True
        >>> keys = store.all()
        >>> print(keys)
        ['key1', 'key2']
        """
        return self.db.all()

    def purge(self) -> bool:
        """
        Clear all keys and values from the database.

        Returns
        -------
        bool
            Always returns True to indicate the operation was performed

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("key1", "value1")
        True
        >>> store.set("key2", "value2")
        True
        >>> store.purge()
        True
        >>> print(store.all())
        []
        """
        return self.db.purge()

    def save(self, option: Optional[int] = None) -> bool:
        """
        Save the current state of the database to file.

        Parameters
        ----------
        option: Optional[int]
            Optional orjson.OPT_* flags that configure serialization behavior.
            These flags can control formatting, special type handling, etc.

        Returns
        -------
        bool
            True if the operation was successful, False otherwise

        Examples
        --------
        >>> store = Store("data.json")
        >>> store.set("key", "value")
        True
        >>> store.save()
        True
        """
        if option is not None:
            return self.db.save(option)
        return self.db.save()
