class Utils:
    def retrieve_client_from_list(user_list, name):
        return next(filter(lambda u: u.name == name, user_list), None)

    def retrieve_group_from_list(group_list, group_id):
        return next(filter(lambda g: g.id == group_id, group_list), None)

    def find_element_index(list, attr, value):
        for i in range(len(list)):
            if getattr(list[i], attr) == value:
                return i
