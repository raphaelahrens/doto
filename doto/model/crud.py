'''
Module for crud operations
'''


def insert(insert_query, cls):
    '''
    Create insert function
    @param insert_query the query for the new insert function
    @param obj_to_row the function to create the row_parameters from the obj
    '''
    def insert_clojure(store, obj_s):
        '''
        Add a new event to the store

        @param store the database store
        @param obj the new event
        '''
        def add_one(obj):
            '''
            Add one row
            '''
            row_parameters = cls.obj_to_row(obj)
            cur = store.execute(insert_query, row_parameters)

            obj.id = cur.lastrowid
            return obj

        try:
            for obj in obj_s:
                add_one(obj)
            return obj_s
        except TypeError:
            return add_one(obj_s)

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
        @param delete_query the query to delete the obj
        '''
        store.execute(delete_query, (obj.id, ))
    return delete_clojure


def update(update_query, cls):
    '''
    Create update function

    @param update_query the query for the new delete function
    @param obj_to_row the function to create the row_parameters from the obj
    '''
    def update_clojure(store, obj):
        '''
        Update the obj

        @param store the database store
        @param obj the event that will be updated
        @param update_query the query that will update the row
        @param obj_to_row function to turn the obj into a row parameters
        '''
        row_dict = cls.obj_to_row(obj)
        store.execute(update_query, row_dict)
        return obj
    return update_clojure
