'''
Module for crud operations
'''


def add_one(store, cls, insert_query, obj):
    '''
    Add one row
    '''
    row_parameters = cls.obj_to_row(obj)
    cur = store.execute(insert_query, row_parameters)

    obj.id = cur.lastrowid
    return obj


def add_and_cache(store, cls, insert_query, obj):
    '''
    Add a new row and store the id and type in the last event cache
    '''
    obj = add_one(store, cls, insert_query, obj)
    store.set_last(obj)
    return obj


def insert(insert_query, cls, add_fn=add_one):
    '''
    Create insert function

    @param insert_query the query for the new insert function
    @param obj_to_row the function to create the row_parameters from the obj
    @param cls the class or module which has a obj_to_row function
    '''
    def insert_clojure(store, obj_s):
        '''
        Add a new event to the store

        @param store the database store
        @param obj the new event
        '''
        try:
            return [add_fn(store, cls, insert_query, obj) for obj in obj_s]
        except TypeError:
            return add_fn(store, cls, insert_query, obj_s)

    return insert_clojure


def delete(delete_query):
    '''
    Create delete function

    @param delete_query the query for the new delete function
    '''
    def delete_clojure(store, obj):
        '''
        Delete an event from the store

        @param store the database store
        @param obj the event that will be deleted
        '''
        store.execute(delete_query, (obj.id, ))
    return delete_clojure


def update(update_query, cls):
    '''
    Create update function

    @param update_query the query for the new delete function
    @param cls the class or module which has a obj_to_row function
    '''
    def update_clojure(store, obj):
        '''
        Update the obj

        @param store the database store
        @param obj the event that will be updated
        '''
        row_dict = cls.obj_to_row(obj)
        store.execute(update_query, row_dict)
        return obj
    return update_clojure


def get(select_query, cls):
    '''
    Create update function

    @param select_query the query which is used to select the object with the id
    @param cls the class or module which has a row_to_obj function
    '''
    def get_clojure(store, select_id):
        '''
        Get one object by its id

        @param store the database store
        @param select_id the id of the obect that shall be fetched
        '''
        return store.get_one(cls.row_to_obj, select_query, {'id': select_id})
    return get_clojure


def get_count(count_query):
    ''' Get the number of rows with the SELECT COUNT(*) query '''
    def get_count_clojure(store):
        ''' Get the count in table of database. '''
        def tuple_to_count(row, _store):
            ''' Extract the first value of the row.  '''
            (count,) = row
            return count
        return store.get_one(tuple_to_count, count_query)

    return get_count_clojure
