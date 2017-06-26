import logging

class Babel:
    #Label babel

    def __init__(self, reporter):
        self.refs = {}
        self.anchors = {}
        self.reporter = reporter

    def add_label(self, label, anchor):
        '''
        This method adds a label and its anchor to the
        babel. The label is unique but can be overwritten.
        '''
        if label in self.anchors:
            logging.warning("Babel @ label: {} already present".format(label))
        #saving the anchor that has to be unique
        self.anchors[label] = anchor
        logging.debug("Babel @ Adding label: \"{}\" to anchor: {}".
                     format(label, anchor))

    def add_reference(self, label, ref):
        '''
        This method adds a reference to the label.
        A reference is a page or in general an object
        with .text properties. The babel will fix the reference
        of the registered objects.
        '''
        #we don't check if label exist because
        #the process is asynchronous"
        if label not in self.refs:
            self.refs[label] = []
        self.refs[label].append(ref)
        logging.debug("Babel @ Adding ref: {}, to label: \"{}\"".
                     format(ref, label))

    def move_anchor(self, oldanc, newanc):
        '''This function replace the references to oldanc with newanc,
        both as anchor and ref. It is used mainly when a page is moved'''
        new_anchors = {}
        for label, anc in self.anchors.items():
            if anc == oldanc:
                new_anchors[label] = newanc
        self.anchors.update(new_anchors)
        new_refs = {}
        for label, ref in self.refs.items():
            if ref == oldanc:
                new_refs[label] = newanc
        self.refs.update(new_refs)


    def fix_references(self):
        '''
        This method will fix the reference in the objects saved under
        self.refs. The text {{ref:label}} in the objects' .text properties
        will be replaces by a url made of [url|title]. The url and the title
        MUST be properties of the anchor saved.
        Finally this method will send to the reporter the references having a
        label without anchor.
        '''
        #iterating over anchor to fix only the right labels
        #and ignoring the missing ones
        for label in self.anchors:
            obj = self.anchors[label]
            title = obj.title
            url = obj.url
            if url is None and title is None:
                continue
            elif url is None and title is not None:
                replace_string = title
            elif url is not None and title is None:
                replace_string = "[["+ url + "]] "
            else:
                replace_string = "[[{}|{}]] ".format(url,title)
            #checking if the babel has refs
            if label not in self.refs:
                continue
            #iterating over all refs
            for ref in self.refs[label]:
                logging.debug("Babel @ Fixing ref to label: \"{}\", from page {} to page: {}".
                             format(label,ref, obj))
                ref.text = ref.text.replace("{{ref@"+ label +"}}", replace_string)
        #checking references without anchors
        for label in self.refs:
            if label not in self.anchors:
                self.reporter.add_missing_anchor(label, self.refs[label])
