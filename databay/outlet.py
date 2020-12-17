"""
.. seealso::

    * :ref:`Extending Outlets <extending_outlets>` to learn how to extend this class correctly.
    * :any:`Inlet` representing the corresponding input of the data stream.


"""
import asyncio
import threading
from abc import ABC, abstractmethod
from typing import List

from databay import Record
import databay as da


class MetadataKey(str):
    """ Used to distinguish class attributes containing metadata keys."""
    pass


class Outlet(ABC):
    """
    Abstract class representing an output of the data stream.
    """

    def __init__(self):
        ""
        self._active = False

        self._uses_coroutine = asyncio.iscoroutinefunction(self.push)

        self._thread_lock = threading.Lock()

    async def _push(self, records: List[Record], update: 'da.Update'):
        if self._uses_coroutine:
            rv = await self.push(records, update)
        else:
            rv = self.push(records, update)

    @abstractmethod
    def push(self, records: List[Record], update: 'da.Update'):
        """
        Push received data.

        Override this method to define how this outlet will handle received data.

        :type records: list[:any:`Record`]
        :param records: List of records generated by inlets. Each top-level element of this array corresponds to one inlet that successfully returned data. Note that inlets could return arrays too, making this a nested array.

        :type update: :any:`Update`
        :param update: Update object representing the particular Link transfer.
        """

        raise NotImplementedError()

    def try_start(self):
        """
        Wrapper around on_start call that will ensure it only gets executed once.
        """

        """ 
        This is a tricky situation we're trying to protect against, and as such this may be redundant.
        The way this is constructed anticipates the on* callback to take very long time, and it prevents
        multiple threads being held waiting for the _thread_lock being released.
        It is questionable whether this function could be called by multiple threads in first place.
        An inlet or outlet would have to be added to multiple links, which in turn would need to be added
        to multiple Planners, all of which would need to request start or shutdown at the same time. 
        Still given how GIL is handled when threading, the race condition may never actually occur.
        We're keeping this logic for now, as it doesn't really waste resources and doesn't inflate complexity
        in any way, while theoretically should protect against callback race conditions, even ones 
        we may not yet be aware of.
        """

        allow_run_on_start = False

        with self._thread_lock:
            if not self._active:
                self._active = True
                allow_run_on_start = True

        if allow_run_on_start:
            self.on_start()

    def on_start(self):
        """
        Called once per outlet just before the governing planner is about to start.

        Override this method to provide starting functionality on this outlet.
        """

        pass

    def try_shutdown(self):
        """
        Wrapper around on_shutdown call that will ensure it only gets executed once.
        """

        """ 
        This is a tricky situation we're trying to protect against, and as such this may be redundant.
        The way this is constructed anticipates the on* callback to take very long time, and it prevents
        multiple threads being held waiting for the _thread_lock being released.
        It is questionable whether this function could be called by multiple threads in first place.
        An inlet or outlet would have to be added to multiple links, which in turn would need to be added
        to multiple Planners, all of which would need to request start or shutdown at the same time. 
        Still given how GIL is handled when threading, the race condition may never actually occur.
        We're keeping this logic for now, as it doesn't really waste resources and doesn't inflate complexity
        in any way, while theoretically should protect against callback race conditions, even ones 
        we may not yet be aware of.
        """

        allow_run_on_shutdown = False

        with self._thread_lock:
            if self._active:
                self._active = False
                allow_run_on_shutdown = True

        if allow_run_on_shutdown:
            self.on_shutdown()

    def on_shutdown(self):
        """
        Called once per outlet just after the governing planner has shutdown.

        Override this method to provide shutdown functionality on this outlet.
        """

        pass

    @property
    def active(self):
        """
        Whether this outlet is active and ready to push. This variable is set automatically to :code:`True` on start and to :code:`False` on shutdown.
        |default| :code:`False`

        :rtype: bool
        """

        return self._active

    def __repr__(self):
        return '%s()' % (self.__class__.__name__)
